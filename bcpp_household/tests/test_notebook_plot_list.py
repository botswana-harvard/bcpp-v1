# from django.test import TestCase
# 
# from bhp066.apps.bcpp_household.classes.notebook_plot_allocation import NotebookPlotAllocation
# 
# 
# class TestNotebookPlotAllocation(TestCase):
# 
#     def test_remove_duplicates_with_load_sharing_evenly1(self):
#         list_with_duplicates = [
#             ['bcpp011', ['21', '22', '23']],
#             ['bcpp038', ['21', '22', '23', '24', '25', '26']],
#             ['bcpp005', ['28', '22', '32', '31', '30']],
#             ['bcpp032', ['48', '42', '42', '41', '40']]
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         list_without_duplicates = notebook.remove_duplicates_and_load_balance_plots
#         self.assertEqual(list(set(['21', '22', '23'])), list_without_duplicates[0][1])
#         self.assertEqual(list(set(['24', '25', '26'])), list_without_duplicates[1][1])
#         self.assertEqual(list(set(['28', '32', '31', '30'])), list_without_duplicates[2][1])
# 
#     def test_remove_duplicates_with_load_sharing_evenly2(self):
#         list_with_duplicates = [
#             ['bcpp011', ['22', '22', '22']],
#             ['bcpp038', ['21', '22', '23', '24', '25', '26']],
#             ['bcpp005', ['28', '22', '32', '31', '30']],
#             ['bcpp032', ['48', '42', '42', '41', '24']]
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         list_without_duplicates = notebook.remove_duplicates_and_load_balance_plots
#         self.assertEqual(list(set(['22'])), list(set(list_without_duplicates[0][1])))
#         self.assertEqual(list(set(['25', '26', '21', '23'])), list_without_duplicates[1][1])
#         self.assertEqual(list(set(['28', '32', '31', '30'])), list_without_duplicates[2][1])
# 
#     def test_remove_duplicates_with_load_sharing_evenly3(self):
#         list_with_duplicates = [
#             ['bcpp011', ['22', '21', '22']],
#             ['bcpp009', ['21', '22', '22']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         list_without_duplicates = notebook.remove_duplicates_and_load_balance_plots
#         self.assertEqual(list(set(['21'])), list(set(list_without_duplicates[0][1])))
#         self.assertEqual(list(set(['22'])), list_without_duplicates[1][1])
# 
#     def test_remove_duplicates_with_load_sharing_evenly4(self):
#         list_with_duplicates = [
#             ['bcpp011', ['22', '21', '23']],
#             ['bcpp009', ['21', '22', '23']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         list_without_duplicates = notebook.remove_duplicates_and_load_balance_plots
#         self.assertEqual(list(set(['21', '23'])), list(set(list_without_duplicates[0][1])))
#         self.assertEqual(list(set(['22'])), list_without_duplicates[1][1])
# 
#     def test_final_list_with_and_cases_shared1(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocated_shared_plots
#         for hosts in new_final_plots:
#             if hosts[0] == 'bcpp011':
#                 self.assertEqual(list(set(['1', '2', '3', '7', '8'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp009':
#                 self.assertEqual(list(set(['4', '5', '6', '9', '10'])), list(set(hosts[1])))
# 
#     def test_final_list_with_and_cases_shared2(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10']],
#             ['bcpp039', ['11', '12', '13', '14']],
#             ['bcpp010', ['15']],
#             ['bcpp012', ['16']],
#             ['bcpp013', ['17']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocated_shared_plots
#         print new_final_plots
#         for hosts in new_final_plots:
#             if hosts[0] == 'bcpp011':
#                 self.assertEqual(list(set(['1', '2', '3', '7', '8'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp009':
#                 self.assertEqual(list(set(['4', '5', '6', '9', '10'])), list(set(hosts[1])))
#                 print hosts[0]
#             elif hosts[0] == 'bcpp010':
#                 self.assertEqual(list(set(['15', '11', '12'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp012':
#                 self.assertEqual(list(set(['16', '13', '14'])), list(set(hosts[1])))
# 
#     def test_final_list_with_and_cases_shared3(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10']],
#             ['bcpp039', ['11', '12', '13', '14']],
#             ['bcpp010', ['15']],
#             ['bcpp012', ['16']],
#             ['bcpp013', ['17', '18']],
#             ['bcpp014', ['19']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocated_shared_plots
#         print new_final_plots
#         for hosts in new_final_plots:
#             if hosts[0] == 'bcpp011':
#                 self.assertEqual(list(set(['1', '2', '3', '7', '8'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp009':
#                 self.assertEqual(list(set(['4', '5', '6', '9', '10'])), list(set(hosts[1])))
#                 print hosts[0]
#             elif hosts[0] == 'bcpp010':
#                 self.assertEqual(list(set(['15', '11', '12'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp012':
#                 self.assertEqual(list(set(['17', '13', '14', '16'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp014':
#                 self.assertEqual(list(set(['18', '19'])), list(set(hosts[1])))
# 
#     def test_final_list_no_plots(self):
#         list_with_duplicates = [
#             ['bcpp011', []],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10']],
#             ['bcpp039', ['11', '12', '13', '14']],
#             ['bcpp010', ['15']],
#             ['bcpp012', ['16']],
#             ['bcpp013', ['17']],
#             ['bcpp014', ['19']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocated_shared_plots
#         for hosts in new_final_plots:
#             if hosts[0] == 'bcpp011':
#                 self.assertEqual(list(set(['7', '8'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp009':
#                 self.assertEqual(list(set(['4', '5', '6', '9', '10'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp010':
#                 self.assertEqual(list(set(['15', '11', '12'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp012':
#                 self.assertEqual(list(set(['13', '14', '16'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp014':
#                 self.assertEqual(list(set(['19', '17'])), list(set(hosts[1])))
# 
#     def test_final_list_no_plots1(self):
#         list_with_duplicates = [
#             ['bcpp011', []],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10']],
#             ['bcpp039', ['11', '12', '13', '14']],
#             ['bcpp010', ['15']],
#             ['bcpp012', []],
#             ['bcpp013', ['17']],
#             ['bcpp014', ['19']],
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocated_shared_plots
#         for hosts in new_final_plots:
#             if hosts[0] == 'bcpp011':
#                 self.assertEqual(list(set(['7', '8'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp009':
#                 self.assertEqual(list(set(['4', '5', '6', '9', '10'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp010':
#                 self.assertEqual(list(set(['15', '11', '12'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp012':
#                 self.assertEqual(list(set(['13', '14'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp014':
#                 self.assertEqual(list(set(['19', '17'])), list(set(hosts[1])))
# 
#     def test_filtering_hosts(self):
#         notebook = NotebookPlotAllocation()
#         available_hosts = [
#             'bcpp011', 'bcpp038', 'bcpp032', 'bcpp008', 'bcpp005', 'bcpp052', 'bcpp016', 'bcpp067']
#         self.assertEqual(list(set(available_hosts)), notebook.filtering_hosts)
# 
#     def test_available_hosts(self):
#         notebook = NotebookPlotAllocation()
#         available_hosts = ['bcpp011', 'bcpp009', 'bcpp067', 'bcpp005', 'bcpp038', 'bcpp016']
#         self.assertEqual(available_hosts, notebook.community_hosts)
# 
#     def test_final_list_with_and_cases(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10', '11']],
#             ['bcpp005', ['12', '13', '14', '15', '16']],
#             ['bcpp052', ['18', '17']],
#             ['bcpp016', ['20', '21']],
#             ['bcpp032', ['19', '22', '23', '24']]
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         list_with_duplicates = notebook.prepare_notebook_plot_list
#         for hosts in list_with_duplicates:
#             if hosts[0] == 'bcpp005':
#                 self.assertEqual(list(set(['12', '13', '14', '15', '16', '18', '17'])), hosts[1])
#             elif hosts[0] == 'bcpp011':
#                 self.assertEqual(list(set(['1', '2', '3'])), hosts[1])
# 
#     def test_final_list_with_and_cases_shared(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10', '11']],
#             ['bcpp005', ['12', '13', '14', '15', '16']],
#             ['bcpp052', ['18', '17']],
#             ['bcpp016', ['20', '21']],
#             ['bcpp032', ['19', '22', '23', '24']],
#             ['bcpp008', ['25', '26', '27', '28']],
#             ['bcpp067', ['62', '61', '63', '64']]
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocated_shared_plots
#         for hosts in new_final_plots:
#             if hosts[0] == 'bcpp067':
#                 self.assertEqual(list(set(['24', '25', '26', '27', '23', '28'])), list(set(hosts[1])))
#             elif hosts[0] == 'bcpp009':
#                 self.assertEqual(list(set(['19', '22', '7', '8', '9', '10', '11'])), list(set(hosts[1])))
# 
#     def test_shared_hosts(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10', '11']],
#             ['bcpp005', ['12', '13', '14', '15', '16']],
#             ['bcpp052', ['18', '17']],
#             ['bcpp016', ['20', '21']],
#             ['bcpp032', ['19', '22', '23', '24']]]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         shared_hosts = notebook.custom_allocation_config_shared
#         self.assertEqual(len(shared_hosts), 2)
# 
#     def test_sections(self):
#         list_with_duplicates = [
#             ['bcpp011', ['1', '2', '3']],
#             ['bcpp009', ['4', '5', '6']],
#             ['bcpp038', ['7', '8', '9', '10', '11']],
#             ['bcpp005', ['12', '13', '14', '15', '16']],
#             ['bcpp052', ['18', '17']],
#             ['bcpp016', ['20', '21']],
#             ['bcpp032', ['19', '22', '23', '24']],
#             ['bcpp008', ['25', '26', '27', '28']],
#             ['bcpp067', ['62', '61', '63', '64']]
#         ]
#         notebook = NotebookPlotAllocation(list_with_duplicates)
#         new_final_plots = notebook.allocate_sections
#         self.assertEqual(['bcpp011 ', ['1', '2', '3'], ['A', 1]], new_final_plots[0])
#         self.assertEqual(['bcpp009', ['19', '22', '7', '8', '9', '10', '11'], ['A', 2]], new_final_plots[1])
