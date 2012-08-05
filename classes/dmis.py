import logging
import pyodbc
import re
from datetime import datetime

from django.conf import settings
from django.db.models import Max

from lab_receive.models import Receive
from lab_order.models import Order
from lab_panel.models import Panel, PanelGroup
from lab_result.models import Result
from lab_result.models import ResultSource
from lab_result_item.models import ResultItem
from lab_test_code.models import TestCode, TestCodeGroup
from lab_common.utils import AllocateResultIdentifier
from lab_aliquot.models import Aliquot
from lab_aliquot_list.models import AliquotType, AliquotCondition, AliquotMedium
from lab_patient.models import Patient
from lab_account.models import Account
from import_history import ImportHistory

from bhp_research_protocol.models import Protocol, Site, Location


logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Dmis(object):

    def __init__(self, lab_db, debug=False, **kwargs):
        self.debug = debug
        self.lab_db = lab_db
        self.dmis_data_source = settings.LAB_IMPORT_DMIS_DATA_SOURCE

    def import_from_dmis(self, **kwargs):
        """Fetches a result from receiving up to the result items.

        ..note:: DMIS has a relational problem with the receiving table LAB01 where multiple
            receiving records can exist for the same primary sample. To correct this on import,
            the receiving record is only imported once while other records (order, result, resultitem)
            are imported complete. Also, LAB21 is not really an order record but there is a 1-many
            relationship between LAB21 and LAB21ResponseQ001x0 which kind of makes it look like one
            even though it was not created by the user as an order. In this script, we create an order and
            a result instance with the same data (LAB21). Result item instances are attached to
            the result instance.
        """
        def receive_row(row):
            """ Holds the receiving record from the DMIS (LAB01). """
            attrs = {'__str__': lambda self: '{0} as of {1}'.format(self.receive_identifier, self.modified),
                     'dmis_reference': row[0],
                    'receive_identifier': row[1],
                    'tid': row[2],
                     'condition': row[3],
                     'visit': row[4],
                     'site_identifier': row[5],
                     'protocol_identifier': row[6],
                    'gender': row[7],
                    'dob': row[8],
                    'subject_identifier': row[9],
                    'initials': row[10],
                    'clinician_initials': row[11],
                    'user_created': row[12],
                    'user_modified': row[13],
                    'receive_datetime': row[14],
                    'drawn_datetime': row[15],
                    'created': row[16],
                    'modified': row[17],
                    'order_identifier': row[18],
                    'panel_id': row[19],
                    'edc_specimen_identifier': row[20],
                    'other_pat_ref': row[21],
                    'site': None,
                    'patient': None,
                    'protocol': None}
            return type('ReceiveRow', (object,), attrs)

        def order_row(row):
            """ Holds the order record from the DMIS (LAB21). """
            attrs = {'__str__': lambda self: '{0} as of {1}'.format(self.order_identifier, self.modified),
                     'dmis_reference': row[0],
                    'receive_identifier': row[1],
                    'tid': row[2],
                    'user_created': row[12],
                    'user_modified': row[13],
                    'order_datetime': row[15],
                    'created': row[16],
                    'modified': row[17],
                    'order_identifier': row[18],
                    'panel': None,
                    'aliquot': None}
            return type('OrderRow', (object,), attrs)

        import_history = ImportHistory(self.lab_db, kwargs.get('subject_identifier', None) or kwargs.get('protocol', None))
        if import_history.start():
            # start with the receiving records. If a receiving record (LAB01) has not been modified
            # on the dmis, nothing further will happen to it nor any of its related data (order, result, resultitem, ...).
            dmis_receive_rows = self._fetch_dmis_receive_rows(import_history, **kwargs)
            if dmis_receive_rows:
                # some of the structure here is to limit the number of calls to the SQL Server
                rowcount = len(dmis_receive_rows)
                received = []
                protocol = None
                sites = {}
                patients = {}
                panel_ids = {}
                accounts = {}
                for dmis_receive_row in dmis_receive_rows:
                    rowcount -= 1
                    if not dmis_receive_row.receive_identifier in received:
                        # for each protocol, site or account check if it is in the list first.
                        # If not, fetch or create and add to the list.
                        received.append(dmis_receive_row.receive_identifier)
                        if not protocol:
                            protocol = self._fetch_or_create(Protocol, dmis_receive_row.protocol_identifier)
                        if dmis_receive_row.site_identifier not in [site_identifier for site_identifier in sites.iterkeys()]:
                            sites[dmis_receive_row.site_identifier] = self._fetch_or_create(Site, dmis_receive_row.site_identifier)
                        if dmis_receive_row.protocol_identifier not in [account_name for account_name in accounts.iterkeys()]:
                            accounts[dmis_receive_row.protocol_identifier] = self._fetch_or_create(Account, dmis_receive_row.protocol_identifier)
                        # for a patient, just fetch or create, no need for a list
                        patients[dmis_receive_row.subject_identifier] = self._create_or_update(Patient,
                            account=accounts[dmis_receive_row.protocol_identifier],
                            subject_identifier=dmis_receive_row.subject_identifier,
                            gender=dmis_receive_row.gender,
                            dob=dmis_receive_row.dob,
                            initials=dmis_receive_row.initials)
                        # pass this row to its own class
                        rcv_row = receive_row(dmis_receive_row)
                        rcv_row.protocol = protocol
                        rcv_row.site = sites[dmis_receive_row.site_identifier]
                        rcv_row.patient = patients[dmis_receive_row.subject_identifier]
                        receive = self._create_or_update(Receive, rcv_row, rowcount)
                        del rcv_row
                    # create or update the order
                    ord_row = order_row(dmis_receive_row)
                    #panel may come from panel_id or tid
                    if dmis_receive_row.panel_id:
                        if dmis_receive_row.panel_id not in [panel_id for panel_id in panel_ids.iterkeys()]:
                            panel_ids[dmis_receive_row.panel_id] = self._fetch_or_create(Panel, panel_id=dmis_receive_row.panel_id,
                                                                                 tid=ord_row.tid,
                                                                                 receive_identifier=receive.receive_identifier)
                        ord_row.panel = panel_ids[dmis_receive_row.panel_id]
                    else:
                        if dmis_receive_row.tid not in [tid for tid in panel_ids.iterkeys()]:
                            panel_ids[dmis_receive_row.tid] = self._fetch_or_create(Panel, panel_id=dmis_receive_row.panel_id,
                                                                            tid=ord_row.tid,
                                                                            receive_identifier=receive.receive_identifier)
                        ord_row.panel = panel_ids[dmis_receive_row.tid]
                    ord_row.aliquot = self._create_or_update(Aliquot, receive, dmis_receive_row.tid)
                    if ord_row.order_identifier:
                        order = self._create_or_update(Order, ord_row)
                        if order:
                            result = self._create_or_update(Result, order)
                            if result:
                                resultitem_rows = self._fetch_dmis_resultitem_rows(result.order.order_identifier)
                                max_validation_datetime = None
                                max_validation_user = None
                                for ritem in resultitem_rows:
                                    result_item = self._create_or_update(ResultItem, result, ritem)
                                    result_item = self._validate_result_item(result, result_item)
                                    if not max_validation_datetime:
                                        max_validation_datetime = result_item.validation_datetime
                                        max_validation_user = result_item.validation_username
                                    if result_item.validation_datetime:
                                        if max_validation_datetime < result_item.validation_datetime:
                                            max_validation_datetime = result_item.validation_datetime
                                            max_validation_user = result_item.validation_username
                                if max_validation_datetime and max_validation_user:
                                    self._release_result(result, max_validation_datetime, max_validation_user)
                                else:
                                    logger.info('    NOT RELEASING {0} resulted on {1}'.format(order.order_identifier, order.order_datetime.strftime("%Y-%m-%d")))

                import_history.finish()
        return None

    def _fetch_or_create(self, cls, value=None, **kwargs):

        def fetch_or_create_protocol(protocol_identifier, lab_db):
            protocols = Protocol.objects.using(lab_db).values('pk').filter(protocol_identifier__iexact=protocol_identifier)
            if protocols:
                protocol = Protocol.objects.using(lab_db).get(protocol_identifier__iexact=protocol_identifier)
            else:
                protocol = Protocol.objects.using(lab_db).create(
                    protocol_identifier=protocol_identifier,
                    research_title='unknown',
                    short_title='unknown',
                    local_title='unknown',
                    date_registered=datetime.today(),
                    date_opened=datetime.today(),
                    description='auto created / imported from DMIS')
            return protocol

        def fetch_or_create_account(account_name, lab_db):
            accounts = Account.objects.using(lab_db).values('pk').filter(account_name__iexact=account_name)
            if accounts:
                account = Account.objects.using(lab_db).get(account_name__iexact=account_name)
            else:
                account = Account.objects.using(lab_db).create(
                    account_name=account_name,
                    account_opendate=datetime.today(),
                    account_closedate=datetime.today(),
                    user_created='auto',
                    created=datetime.today(),
                    comment='auto created / imported from DMIS')
                account.save()
            return account

        def fetch_or_create_panel(lab_db, dmis_data_source, **kwargs):
            panel_id = kwargs.get('panel_id')
            tid = kwargs.get('panel_id')
            receive_identifier = kwargs.get('receive_identifier')
            panel = None
            panel_group_name = None
            # use either panel_id or panel_group_name to either get or create a panel
            # if you have receive_identifier, this may help
            if panel_id and not panel_id == '-9':
                # try to get using row.panel_id
                panels = Panel.objects.using(lab_db).filter(dmis_panel_identifier=panel_id)
                if panels:
                    panel = panels[0]
            if not panel and tid:
                panels = Panel.objects.using(lab_db).filter(dmis_panel_identifier__exact=tid)
                if panels:
                    panel = panels[0]
            if not panel and receive_identifier:
                # go back to the receving record and get the TID of the first record,
                # usually only one record returned, but not always...
                cnxn1 = pyodbc.connect(dmis_data_source)
                cursor_panel = cnxn1.cursor()
                sql = 'select top 1 tid as panel_group_name from lab01response where pid=\'%s\' order by datecreated' % (receive_identifier,)
                cursor_panel.execute(str(sql))
                for row in cursor_panel:
                    panel_group_name = row.panel_group_name
                    panels = Panel.objects.using(lab_db).filter(panel_group__name__exact=panel_group_name)
                    if panels:
                        panel = panels[0]
            if not panel:
                raise TypeError(panel_id)
                # hmmm. still nothing, so just create a dummy panel and move on
                panel_groups = PanelGroup.objects.using(lab_db).filter(name=panel_id)
                if not panel_groups:
                    panel_group = PanelGroup.objects.using(lab_db).create(name=panel_id,)
                else:
                    panel_group = PanelGroup.objects.using(lab_db).get(name=panel_id,)
                # create a new panel
                panel = Panel.objects.using(lab_db).create(
                    name=panel_id,
                    panel_group=panel_group,
                    comment='temp',
                    dmis_panel_identifier=panel_id)
                logger.info('  created panel for %s ' % (panel_id,))
            return panel

        def fetch_or_create_resultsource(lab_db, **kwargs):
            interfaces = ['psm_interface', 'cd4_interface', 'auto', 'manual_entry', 'direct_import', ]
            agg = ResultSource.objects.using(self.lab_db).aggregate(Max('display_index'),)
            display_index = 0
            if agg:
                display_index = agg['display_index__max'] or 0
            # populate if not already ...
            for interface in interfaces:
                if not ResultSource.objects.using(lab_db).filter(name__iexact=interface):
                    result_source = ResultSource.objects.using(lab_db).create(
                        name=interface,
                        short_name=interface,
                        display_index=display_index + 10,
                        )
                    result_source.save()
            # create a new one if given argument and does not exist already
            if kwargs.get('interface'):
                if not ResultSource.objects.using(lab_db).filter(name__iexact=kwargs.get('interface')):
                    result_source = ResultSource.objects.using(lab_db).create(
                        name=kwargs.get('interface'),
                        short_name=kwargs.get('interface'),
                        display_index=display_index + 11,
                        )
                    result_source.save()
                else:
                    result_source = ResultSource.objects.using(lab_db).get(name__iexact=kwargs.get('interface'))
            else:
                result_source = None
            return result_source

        def fetch_or_create_site(site_identifier, lab_db):
            if site_identifier == None or site_identifier == '' or site_identifier == '-9':
                site_identifier = '00'
            sites = Site.objects.using(lab_db).values('pk').filter(site_identifier__iexact=site_identifier)
            if sites:
                site = Site.objects.using(lab_db).get(site_identifier__iexact=site_identifier)
            else:
                location = Location.objects.using(lab_db).values('pk').filter(name__exact='UNKNOWN')
                if location:
                    location = Location.objects.using(lab_db).get(name__exact='UNKNOWN')
                else:
                    location = Location.objects.using(lab_db).create(name='UNKNOWN')
                site = Site.objects.using(lab_db).create(site_identifier=site_identifier, name=site_identifier, location=location)
            return site

        if cls == Protocol:
            return fetch_or_create_protocol(value, self.lab_db)
        elif cls == Account:
            return fetch_or_create_account(value, self.lab_db)
        elif cls == Panel:
            return fetch_or_create_panel(self.lab_db, self.dmis_data_source, **kwargs)
        elif cls == ResultSource:
            return fetch_or_create_resultsource(self.lab_db, **kwargs)
        elif cls == Site:
            return fetch_or_create_site(value, self.lab_db)
        else:
            raise TypeError('Expected and instance of Protocol, Account or Panel. Got {0}'.format(cls))

    def _create_or_update(self, cls, *args, **kwargs):

        lab_db = self.lab_db
        dmis_data_source = self.dmis_data_source

        def create_or_update_receive(row, rowcount):
            #is this receiving record on file
            receives = Receive.objects.using(lab_db).values('pk').filter(receive_identifier=row.receive_identifier)
            if receives:
                receive = Receive.objects.using(lab_db).get(receive_identifier=row.receive_identifier)
                if receive.modified < row.modified:
                    receive.modified = row.modified
                    receive.user_modified = row.user_modified
                    receive.protocol = row.protocol
                    receive.drawn_datetime = row.drawn_datetime
                    receive.receive_datetime = row.receive_datetime
                    receive.site = row.site
                    receive.visit = row.visit
                    receive.clinician_initials = row.clinician_initials
                    receive.dmis_reference = row.dmis_reference
                    receive.requisition_identifier = row.edc_specimen_identifier or row.other_pat_ref
                    receive.receive_condition = row.condition
                    receive.save()
                    logger.info('  dmis - receive: {rowcount} sample {receive_identifier} exists and updating '
                                'for {subject_identifier}.'.format(rowcount=rowcount,
                                                                   receive_identifier=row.receive_identifier,
                                                                   subject_identifier=row.subject_identifier))
                else:
                    logger.info('  dmis - receive: {rowcount} sample {receive_identifier} exists but not modified for '
                                '{subject_identifier}.'.format(rowcount=rowcount,
                                                               receive_identifier=row.receive_identifier,
                                                               subject_identifier=row.subject_identifier))
            else:
                receive = Receive.objects.using(lab_db).create(
                    protocol=row.protocol,
                    receive_identifier=row.receive_identifier,
                    patient=row.patient,
                    site=row.site,
                    visit=row.visit,
                    drawn_datetime=row.drawn_datetime,
                    receive_datetime=row.receive_datetime,
                    user_created=row.user_created,
                    user_modified=row.user_modified,
                    created=row.created,
                    modified=row.modified,
                    dmis_reference=row.dmis_reference,
                    clinician_initials=row.clinician_initials,
                    requisition_identifier=row.edc_specimen_identifier or row.other_pat_ref,
                    receive_condition=row.condition)
                logger.info('  dmis - receive: {rowcount} creating '
                            '{receive_identifier} for {subject_identifier}'.format(rowcount=rowcount,
                                                                                   receive_identifier=row.receive_identifier,
                                                                                   subject_identifier=row.subject_identifier))
            return receive

        def create_or_update_order(row):
            orders = Order.objects.using(lab_db).filter(order_identifier=row.order_identifier)
            if orders:
                order = Order.objects.using(lab_db).get(order_identifier=row.order_identifier)
                logger.info('    order: found existing {order_identifier}'.format(order_identifier=row.order_identifier))
            else:
                order = Order.objects.using(lab_db).create(
                    order_identifier=row.order_identifier,
                    order_datetime=row.order_datetime,
                    aliquot=row.aliquot,
                    panel=row.panel,
                    comment='',
                    created=row.created,
                    modified=row.modified,
                    user_created=row.user_created,
                    user_modified=row.user_modified,
                    dmis_reference=row.dmis_reference,
                    )
                logger.info('    order: created {order_identifier}'.format(order_identifier=row.order_identifier))
            return order

        def create_or_update_result(order):
            """ Updates the dmis result using the given \'order\' by querying the dmis server on the order_identifier for
            a dmis result (LAB21) that has result_items (LAB21D)"""
            cnxn2 = pyodbc.connect(dmis_data_source)
            cursor_result = cnxn2.cursor()
            result = Result.objects.using(lab_db).filter(order=order).order_by('-modified')
            if result:
                if result.count() > 1:
                    # get rid of duplicates
                    logger.warning('    result: warning: more than one result found for %s' % (result[0].result_identifier,))
                # take most recent
                result = Result.objects.using(lab_db).filter(order=order).order_by('-modified')[0]
                logger.warning('    result: result found for {0} resulted on {1}'.format(order.order_identifier, result.result_datetime.strftime("%Y-%m-%d")))
            else:
                # create new result
                # fetch the order/result from DMIS (note in DMIS orders are generated when a
                # result is available so orders always have results)
                sql = ('select distinct headerdate as result_datetime, '
                       'l21.keyopcreated as user_created, '
                       'l21.datecreated as created, '
                       'convert(varchar(36), l21.result_guid) as result_guid '
                       'from BHPLAB.DBO.LAB21Response as L21 '
                       'left join BHPLAB.DBO.LAB21ResponseQ001X0 as L21D on L21.Q001X0=L21D.QID1X0 '
                       'where l21.id=\'{order_identifier}\' and '
                       'l21d.id is not null').format(order_identifier=order.order_identifier)
                cursor_result.execute(str(sql))  # should return 0 or 1 row because l21.id is a primary key
                n = 0
                for row in cursor_result:
                    n += 1
                    # allocate a result identifier for this new result
                    result_identifier = AllocateResultIdentifier(order)
                    if n > 1:
                        logger.warning('    result: warning - more than one result created for {0}'.format(order.order_identifier,))
                    # create the result record
                    result = Result.objects.using(lab_db).create(
                        result_identifier=result_identifier,
                        order=order,
                        result_datetime=row.result_datetime,
                        comment='',
                        user_created=row.user_created,
                        created=row.created,
                        dmis_result_guid=row.result_guid)
                    logger.info('    result: created result for order {0} resulted on {1}'.format(order.order_identifier, order.order_datetime.strftime("%Y-%m-%d")))
                    self._fetch_or_create(ResultSource)
                    # create or update the result items for this result
            return result

        def create_or_update_resultitem(result, ritem):
            """ Creates a result item for the given ritem from the dmis.

            ..note:: dmis item overwrites and existing django-lis item. The dmis sql statement is
            ordered on datelastmodified which means oldest testcodes will come in first
            and later be overwritten by the same testcode if a testcode appears more than once for a result.
            """
            def fetch_or_create_testcode(code, lab_db):
                try:
                    test_code = TestCode.objects.using(lab_db).get(code__exact=code)
                except:
                    test_code_group = TestCodeGroup.objects.using(lab_db).get(code__exact='000')
                    TestCode.objects.using(self.lab_db).create(
                        code=code,
                        name=code,
                        units='-',
                        test_code_group=test_code_group,
                        display_decimal_places=0,
                        is_absolute='absolute',
                        )
                    test_code = TestCode.objects.using(self.lab_db).get(code__iexact=code)
                return test_code

            def get_ritem_user(dmis_user):
                # change NT system username to auto
                if dmis_user.strip(' \t\n\r').upper() == 'NT AUTHORITY\SYSTEM':
                    user = 'auto'
                else:
                    user = dmis_user
                return user

            def get_ritem_validation(ritem):
                result_item_source = ''
                result_item_source_reference = ''
                validation_reference = ''
                # evaluate validation_reference
                if ritem.validation_reference == '-9':
                    # this is an item from GetResults TCP connected to PSM
                    result_item_source = self._fetch_or_create(ResultSource, interface='psm_interface')
                    result_item_source_reference = ''
                    validation_reference = 'dmis-auto'
                elif ritem.validation_reference == 'LAB21:MANUAL':
                    # manual entry and no validation -- straight to LAB21 tableset
                    result_item_source = self._fetch_or_create(ResultSource, interface='manual_entry')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'auto'
                elif re.search('^rad[0-9A-F]{5}\.tmp$', ritem.validation_reference):
                    # this is an item from GetResults Flatfile and validated via the LAB05 path
                    result_item_source = self._fetch_or_create(ResultSource, interface='cd4_interface')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'lab05'
                elif re.search('^LAB23:', ritem.validation_reference):
                    # manual entry and validated via the LAB23 validation path
                    result_item_source = self._fetch_or_create(ResultSource, interface='manual_entry')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'lab23'
                elif re.search('^IMPORT', ritem.validation_reference):
                    # manual entry and validated via the LAB23 validation path
                    result_item_source = self._fetch_or_create(ResultSource, interface='direct_import')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'auto'
                elif re.search('^LB003:', ritem.validation_reference):
                    # manual import
                    result_item_source = self._fetch_or_create(ResultSource, interface='direct_import')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'auto'
                elif re.search('^LB004:', ritem.validation_reference):
                    # manual import
                    result_item_source = self._fetch_or_create(ResultSource, interface='direct_import')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'auto'
                elif re.search('^[0-9]{2}\/[0-9]{2}\/[0-9]{4}$', ritem.validation_reference):
                    # manual import
                    result_item_source = self._fetch_or_create(ResultSource, interface='manual_entry')
                    result_item_source_reference = 'dmis-%s' % ritem.validation_reference
                    validation_reference = 'auto'
                else:
                    # missed a case? let's hear about it
                    raise TypeError('Validation reference \'%s\' was not expected. See dmis_fetch_result.' % ritem.validation_reference)
                result_item_source_reference = '%s %s' % (result_item_source_reference, ritem.mid)
                return {'validation_reference': validation_reference,
                        'result_item_source': result_item_source,
                        'result_item_source_reference': result_item_source_reference}

            code = ritem.code.strip(' \t\n\r')
            # delete from django-lis the one result item for this result (should only be one)
            ResultItem.objects.using(self.lab_db).filter(result=result, test_code__code=code).delete()
            test_code = fetch_or_create_testcode(code, lab_db)
            user = get_ritem_user(ritem.user_created)
            validation = get_ritem_validation(ritem)
            # create a new result item. set validation to 'P', we'll import
            # full validation information later
            result_item = ResultItem.objects.using(self.lab_db).create(
                result=result,
                test_code=test_code,
                result_item_datetime=ritem.result_item_datetime,
                result_item_value=ritem.result_value,
                result_item_quantifier=ritem.result_quantifier,
                validation_status='P',
                validation_reference=validation['validation_reference'],
                result_item_source=validation['result_item_source'],
                result_item_source_reference=validation['result_item_source_reference'],
                result_item_operator=user,
                comment='',
                )
            logger.info('      created item {0}'.format(code, ritem.result_item_datetime.strftime("%Y-%m-%d")))
            return result_item

        def create_or_update_patient(**kwargs):
            subject_identifier = kwargs.get('subject_identifier').strip(' \t\n\r')
            initials = kwargs.get('initials').strip(' \t\n\r')
            if not initials:
                initials = 'X0X'
            account = kwargs.get('account')
            gender = kwargs.get('gender')
            dob = kwargs.get('dob')
            is_dob_estimated = '-'
            patients = Patient.objects.using(lab_db).values('pk').filter(subject_identifier__iexact=subject_identifier)
            if patients:
                patient = Patient.objects.using(lab_db).get(subject_identifier__iexact=subject_identifier)
                patient.dob = dob
                patient.gender = gender
                patient.is_dob_estimated = is_dob_estimated
                patient.initials = initials
                patient.save()
            else:
                patient = Patient.objects.using(lab_db).create(
                    subject_identifier=subject_identifier,
                    initials=initials,
                    gender=gender,
                    dob=dob,
                    is_dob_estimated=is_dob_estimated,
                    comment='auto created / imported from DMIS')
                patient.account.add(account)
            return patient

        def create_or_update_aliquot(receive, tid):

            def create_or_update_aliquotcondition(condition, lab_db):
                if AliquotCondition.objects.using(lab_db).values('pk').filter(short_name__exact=condition):
                    aliquot_condition = AliquotCondition.objects.using(lab_db).get(short_name__exact=condition)
                else:
                    agg = AliquotCondition.objects.using(lab_db).aggregate(Max('display_index'),)
                    if not agg:
                        display_index = 10
                    else:
                        display_index = agg['display_index__max'] + 10
                    aliquot_condition = AliquotCondition.objects.using(lab_db).create(
                        name=condition,
                        short_name=condition,
                        display_index=display_index,
                        )
                    aliquot_condition.save()
                return aliquot_condition

            if receive.receive_condition:
                aliquot_condition = create_or_update_aliquotcondition(receive.receive_condition, lab_db)
            else:
                aliquot_condition = None
            #create primary
            # TODO: need more detail here for sample types other than the ones listed here...
            create = {}
            if tid == '411':
                create['type'] = '02'  # WB
                create['medium'] = 'DBS'
            else:
                create['type'] = '02'  # WB
                create['medium'] = 'TUBE'
            # get or create the primary aliquot
            aliquot_identifier = '%s0000%s01' % (receive.receive_identifier, create['type'])
            if Aliquot.objects.using(lab_db).values('pk').filter(aliquot_identifier__iexact=aliquot_identifier):
                primary_aliquot = Aliquot.objects.using(lab_db).get(aliquot_identifier__iexact=aliquot_identifier)
                if not primary_aliquot.modified == receive.modified:
                    aliquot_type = AliquotType.objects.using(lab_db).get(numeric_code__exact=create['type'])
                    primary_aliquot.modified = receive.modified
                    primary_aliquot.aliquot_type = aliquot_type
                    primary_aliquot.condition = aliquot_condition
                    primary_aliquot.save()
            else:
                create['comment'] = 'auto created on import from DMIS'
                aliquot_type = AliquotType.objects.using(lab_db).get(numeric_code__exact=create['type'])
                aliquot_medium = AliquotMedium.objects.using(lab_db).get(short_name__iexact=create['medium'])
                primary_aliquot = Aliquot.objects.using(lab_db).create(
                    aliquot_identifier=aliquot_identifier,
                    receive=receive,
                    count=1,
                    aliquot_type=aliquot_type,
                    medium=aliquot_medium,
                    condition=aliquot_condition,
                    comment=create['comment'],
                    )
            return primary_aliquot

        if cls == Patient:
            return create_or_update_patient(**kwargs)
        elif cls == Aliquot:
            return create_or_update_aliquot(args[0], args[1])
        elif cls == Receive:
            return create_or_update_receive(args[0], args[1])
        elif cls == Order:
            return create_or_update_order(args[0])
        elif cls == Result:
            return create_or_update_result(args[0])
        elif cls == ResultItem:
            return create_or_update_resultitem(args[0], args[1])
        else:
            raise TypeError('Expected and instance of Protocol, Account or Panel. Got {0}'.format(cls))

    def _validate_result_item(self, result, result_item, **kwargs):
        """ Imports result item validation information from the dmis.

        ..note:: For legacy reasons, dmis has more than one approach to capturing validation information. For
        CD4 results the LAB05 path is used, while for all other results the LAB23 path id used. Additionally, for
        results that are auto validated, like those coming from PSM, the information comes from LAB21 directly.
        """
        def _validate_l21(result_item, result):
            result_item.result_item_operator = result.user_created.strip('BHP\\bhp\\')
            result_item.validation_status = 'F'
            result_item.validation_datetime = result_item.result_item_datetime or result_item.validation_datetime
            result_item.validation_username = 'auto'
            result_item.save()

        def _validate_l23(result_item, row):
            result_item.result_item_operator = row.operator.strip('BHP\\bhp\\')
            result_item.validation_status = 'F'
            result_item.validation_datetime = row.validation_datetime
            result_item.validation_username = row.validation_username.strip('BHP\\bhp\\')
            result_item.save()

        def _validate_l5(result_item, row):
            _validate_l23(result_item, row)

        cnxn2 = pyodbc.connect(self.dmis_data_source)
        cursor_result = cnxn2.cursor()
        # if you know the 'interface' then you know how validation occurs
        cd4_interface = ResultSource.objects.using(self.lab_db).get(name__iexact='cd4_interface')
        psm_interface = ResultSource.objects.using(self.lab_db).get(name__iexact='psm_interface')
        direct_interface = ResultSource.objects.using(self.lab_db).get(name__iexact='direct_import')
        manual_interface = ResultSource.objects.using(self.lab_db).get(name__iexact='manual_entry')
        #the validation process depends on the 'interface'.
        if result_item.result_item_source == psm_interface:
            _validate_l21(result_item, result)
        elif result_item.result_item_source == direct_interface:
            _validate_l21(result_item, result)
        elif result_item.result_item_source == cd4_interface:
            #this returns only one record per result, only, so update all items as one
            # hmmm ... all imported results are from LAB21 which implies result_accepted=1, add "where result_accepted=1"
            sql = "select top 1 result_accepted_username as operator, \
                    result_accepted_username as validation_username, \
                    l5.result_accessed_date as validation_datetime, \
                    archive_filename+' ('+exp_filename+')' as result_item_source_reference \
                    from bhplab.dbo.lab05response as l5 \
                    left join bhplab.dbo.results_101 as r101 on l5.result_guid=r101.result_guid \
                    where result_accepted=1 and convert(varchar(36),l5.result_guid)='%s'" % result.dmis_result_guid

            cursor_result = cnxn2.cursor()
            cursor_result.execute(str(sql))
            for row in cursor_result:
                _validate_l5(result_item, row)
        elif result_item.result_item_source == manual_interface and result_item.validation_reference.lower() != 'lab23':
            _validate_l21(result_item, result)
        elif result_item.result_item_source == manual_interface and result_item.validation_reference.lower() == 'lab23':
            #this returns one record per result, only, so update all items as one
            sql = ('select lower(L23.operator) as operator, '
                   'lower(l23d.checkbatch_user) as validation_username, '
                   'l23d.datelastmodified as validation_datetime, '
                   'convert(varchar, l23.id) as validation_reference '
                   'from bhplab.dbo.lab23response as l23 '
                   'left join bhplab.dbo.lab23responseq001x0 as l23d on l23.q001x0=l23d.qid1x0 '
                   'where result_accepted=1 and upper(ltrim(rtrim(utestid)))=\'{code}\' and '
                   'convert(varchar(36),result_guid)=\'{result_guid}\'').format(code=result_item.test_code.code,
                                                                                result_guid=result.dmis_result_guid)
            cursor_result = cnxn2.cursor()
            cursor_result.execute(str(sql))
            for row in cursor_result:
                _validate_l23(result_item, row)
        else:
            raise TypeError('Unknown case result_item_source in dmis validation. '
                            'Got \'%s\' from result %s.' % (result.resultitem.result_item_source, result))
        logger.info('      validated item %s %s' % (result_item.test_code.code, result_item.result_item_source))
        return result_item

    def _release_result(self, result, validation_datetime, validation_username, **kwargs):

        if not validation_datetime:
            raise TypeError('Expected a date for validation_datetime for '
                            'result {0}. Got None.'.format(result.result_identifier))
        if validation_username == 'auto' or not validation_username:
            validation_username = unicode('smoyo')

        # remove oldest of any duplicate result_items

        # update result
        result.release_status = 'RELEASED'
        result.release_datetime = validation_datetime
        result.release_username = validation_username
        result.save()
        logger.info('      released by {validation_username} on '
                    '{validation_datetime}'.format(validation_username=validation_username,
                                                   validation_datetime=validation_datetime))

    def _fetch_dmis_receive_rows(self, import_history, **kwargs):

        def _get_dmis_receive_where_clause(clause=None, **kwargs):
            subject_identifier = kwargs.get('subject_identifier', None)
            protocol = kwargs.get('protocol', None)
            where_clause = []
            if clause:
                where_clause.append(clause)
            if subject_identifier:
                where_clause.append('l.pat_id like \'%{subject_identifier}%\''.format(subject_identifier=subject_identifier))
            if protocol:
                where_clause.append('sample_protocolnumber=\'{protocol}\''.format(protocol=protocol))
            if where_clause:
                where_clause = 'where {0}'.format(' and '.join(where_clause))
            else:
                where_clause = ''
            return where_clause

        subject_identifier = kwargs.get('subject_identifier', None)
        protocol = kwargs.get('protocol', None)
        cnxn = pyodbc.connect(self.dmis_data_source)
        cursor = cnxn.cursor()
        where_clause = _get_dmis_receive_where_clause(import_history.conditional_clause, **kwargs)
        if where_clause is None:
            where_clause = ''
        sql = ('select '
               'l.id as dmis_reference,'
                'l.pid as receive_identifier, '
                'l.tid, '
                'l.sample_condition,'
                'l.sample_visitid as visit,'
                'l.sample_site_id as site_identifier,'
                'l.sample_protocolnumber as protocol_identifier,'
                'l.gender,'
                'dob as dob,'
                'l.pat_id as subject_identifier,'
                'l.pinitials as initials, '
                'l.cinitials as clinician_initials, '
                'l.keyopcreated as user_created,'
                'l.keyoplastmodified as user_modified,'
                'l.headerdate as receive_datetime, '
                'l.sample_date_drawn as drawn_datetime,'
                'l.datecreated as created, '
               ' l.datelastmodified as modified,'
                'l21.id as order_identifier,'
                'l21.panel_id, '
                'l.edc_specimen_identifier, '
                'l.other_pat_ref '
                'from lab01response as l '
                'left join lab21response as l21 on l.pid=l21.pid '
                ' {where_clause} '
                'order by l.pat_id, l.datelastmodified desc').format(where_clause=where_clause)
        rows = cursor.execute(str(sql)).fetchall()
        if len(rows) == 0:
            logger.info('  dmis - receive: nothing received for {subject_identifier}'
                        '{protocol} since '
                        '{last_import_datetime}.'.format(subject_identifier=subject_identifier or '',
                                                   protocol=protocol or '',
                                                   dmis_data_source='lab',
                                                   last_import_datetime=import_history.last_import_datetime))
        return rows

    def _fetch_dmis_resultitem_rows(self, order_identifier):
        # get list of result items for this result from DMIS (LAB21ResponseQ001X0)
        # order by datelastmodified so that if there is more than one value for a
        # testcode, the youngest will overwrite the older ones.
        cnxn3 = pyodbc.connect(self.dmis_data_source)
        cursor_resultitem = cnxn3.cursor()
        sql = ('select l21d.sample_assay_date, '
                'utestid as code,'
                'result as result_value, '
                'result_quantifier, '
                'status, '
                'mid,'
                'l21d.validation_ref as validation_reference, '
                'l21d.datelastmodified as result_item_datetime, '
                'l21d.keyopcreated as user_created, '
                'l21d.keyoplastmodified as user_modified, '
                'l21.datecreated as created, '
                'l21.datelastmodified as modified '
                'from BHPLAB.DBO.LAB21Response as L21 '
                'left join BHPLAB.DBO.LAB21ResponseQ001X0 as L21D on L21.Q001X0=L21D.QID1X0 '
                'where l21.id=\'%s\' and l21d.id is not null order by l21d.datelastmodified') % order_identifier
        return cursor_resultitem.execute(str(sql))
