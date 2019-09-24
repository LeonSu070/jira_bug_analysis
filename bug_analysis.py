from module.analysis_util import the_closest_sprint_start_date, get_the_last_sprint_bugs, debug_log_console
from module.jba_email import send_email_from_graphics
from module.jira_bug import JiraBugList
from module.jira_method import is_system_available, system_init, get_fields_in_dict
from module.pyplot_util import *
from module.pyplot_util import bug_data_and_label_classified_in_catalog
from module.storage_util import *
from module.sys_invariant import date_format, show_last_n_bars, get_online_bug_summary_png_filename, \
    get_sprint_bug_summary_filename, online_bug_priority_png, online_bug_classification_png, \
    online_bug_unclassified_png, online_bug_source_in_csv, online_bug_team_png
from pprint import pprint

def store_count_into_file(sprint_bug_summary_filename, last_sprint_bugs_count, tech_bug_amount, sprint_start_date):
    file_backup(sprint_bug_summary_filename)
    sprint_online_bug_summary_json_data = read_json_from_file(sprint_bug_summary_filename)
    if sprint_online_bug_summary_json_data is "":
        return ""
    sprint_online_bug_summary_json_data = append_latest_sprint_info(last_sprint_bugs_count, tech_bug_amount, 
                                                                    sprint_online_bug_summary_json_data,
                                                                    sprint_start_date)
    pprint(sprint_online_bug_summary_json_data)
    write_json_obj_to_file(sprint_bug_summary_filename, sprint_online_bug_summary_json_data)
    return sprint_online_bug_summary_json_data


def append_latest_sprint_info(last_sprint_bugs_count, tech_bug_amount, sprint_online_bug_summary_json_data, sprint_start_date):
    debug_log_console(str(sprint_online_bug_summary_json_data))
    is_updated = False
    sprint_start_date_str = datetime.datetime.strftime(sprint_start_date, date_format["in_file"])
    for sprint_summary in sprint_online_bug_summary_json_data:
        if sprint_summary["sprint date"] == sprint_start_date_str:
            sprint_summary["sprint bug count"] = last_sprint_bugs_count
            sprint_summary["tech bug count"] = tech_bug_amount
            is_updated = True
            break
    if not is_updated:
        sprint_online_bug_summary_json_data.append(
            {"sprint date": sprint_start_date_str,
             "sprint bug count": last_sprint_bugs_count,
             "tech bug count": tech_bug_amount})
    return sprint_online_bug_summary_json_data


def generate_online_bug_summary_chart(sprint_bug_summary_json, filename):
    dates, counts, counts_2 = convert_summary_into_dates_and_counts(sprint_bug_summary_json)
    debug_log_console(dates)
    return generate_bar_chart(dates, counts, counts_2, filename)

def convert_summary_into_dates_and_counts(sprint_bug_summary_json):
    dates = []
    counts = []
    counts_2 = []
    for sprint_bug in sprint_bug_summary_json:
        dates.append(sprint_bug["sprint date"])
        counts.append(sprint_bug["sprint bug count"])
        if "tech bug count" in sprint_bug :
            counts_2.append(sprint_bug["tech bug count"])
        else:
            counts_2.append(0)
    return dates[show_last_n_bars:], counts[show_last_n_bars:], counts_2[show_last_n_bars:]

def get_tech_bug_amount(last_sprint_bugs):
    amount = 0
    for bug in last_sprint_bugs:
        if bug['bug classify'] != "Wrong Reported" :
            amount = amount + 1
    return amount

def generate_bug_summary_barchart(bug_list):
    # find the latest sprint bugs
    last_sprint_bugs, sprint_start_date = get_the_last_sprint_bugs(bug_list)
    debug_log_console(str(sprint_start_date))
    
    #get tech bug amount
    tech_bug_amount = get_tech_bug_amount(last_sprint_bugs)

    # store the count into file
    sprint_bug_summary_json = store_count_into_file(get_sprint_bug_summary_filename(), len(last_sprint_bugs), tech_bug_amount,
                                                    sprint_start_date)

    if sprint_bug_summary_json is "":
        return None

    # generate chart
    return generate_online_bug_summary_chart(sprint_bug_summary_json, get_online_bug_summary_png_filename())


def get_bug_list(basic_base64_token):
    fields = get_fields_in_dict(basic_base64_token)
    sprint_start_date = the_closest_sprint_start_date(datetime.datetime.now())
    bug_list = JiraBugList(sprint_start_date, basic_base64_token, fields)

    is_list_fetched_successful = bug_list.fetch_list_from_jira()
    if not is_list_fetched_successful:
        return None
    print("total bugs: " + str(len(bug_list.bugs)))
    return bug_list


def generate_bug_priority_barhchart(bug_list):
    priority_data, priority_label = bug_data_and_label_classified_in_catalog(bug_list,
                                                                             ["Low", "Medium", "High", "Highest"],
                                                                             'priority')
    debug_log_console(str(priority_data))
    debug_log_console(str(priority_label))
    return generate_barh_chart(priority_label, priority_data, online_bug_priority_png)


def generate_bug_classification_piechart(bug_list):
    classify_data, classify_label = bug_data_and_label_classified_in_catalog(bug_list,
                                                                             ["Fore-End", "Product Logic", "Server",
                                                                              "Third Part", "Wrong Reported"],
                                                                             'bug classify')
    debug_log_console(str(classify_data))
    debug_log_console(str(classify_label))
    return generate_pie_chart(classify_label, classify_data, online_bug_classification_png, "Classification")


def generate_bug_unclassified_piechart(bug_list):
    classify_data, classify_label = bug_data_and_label_classified_in_catalog(bug_list,
                                                                             ["Fore-End", "Product Logic", "Server",
                                                                              "Third Part", "Wrong Reported"],
                                                                             'bug classify')
    unclassified_label = ["Clarified", "Non-Clarified"]
    unclassified_data = [sum(classify_data), (len(bug_list.bugs) - sum(classify_data))]
    debug_log_console(str(unclassified_label))
    debug_log_console(str(unclassified_data))
    return generate_pie_chart(unclassified_label, unclassified_data, online_bug_unclassified_png, "Unclassified")


def generate_bug_team_barchart(bug_list):
    team_data, team_label = bug_data_and_label_classified_in_catalog_pro(bug_list, 'bug classify', 'scrum team')

    debug_log_console(str(team_data))
    debug_log_console(str(team_label))
    colors = {
                'Wrong Reported':'purple',
                'Others':'yellow',
                'Fore-End':'blue',
                'Product Logic':'orange',
                'Server':'green',
                'Third Part':'red'
            }
    return generate_barsuperpose_chart(team_label, team_data, colors, "Team bugs", online_bug_team_png)


def write_bug_list_to_csv(bug_list):
    if bug_list.bugs[0] is None:
        return
    column_header = bug_list.bugs[0].keys()
    return write_to_csv(column_header, bug_list.bugs, online_bug_source_in_csv)


def do_bug_analysis():
    basic_base64_token = system_init()
    if not is_system_available(basic_base64_token):
        print("system check failed, please ask admin")
        return

    bug_list = get_bug_list(basic_base64_token)

    # No.1 graphic - bug summary
    summary_barchart = generate_bug_summary_barchart(bug_list)
    debug_log_console("summary bar chart image generated")

    # No.2 graphic - bug priority
    priority_barchart = generate_bug_priority_barhchart(bug_list)
    debug_log_console("priority bar chart filename generated")

    # No.3 graphic - bug classification
    classification_piechart = generate_bug_classification_piechart(bug_list)
    debug_log_console("classification bar chart filename generated")

    # No.4 graphic - bug unclassified
    unclassified_piechart = generate_bug_unclassified_piechart(bug_list)
    debug_log_console("unclassified pie chart filename generated")

    # No.5 graphic - bug team
    team_barchart = generate_bug_team_barchart(bug_list)
    debug_log_console("team bug chart filename generated")

    online_bug_source = write_bug_list_to_csv(bug_list)
    #debug_log_console(online_bug_source.decode("utf-8"))

    # final step - compose and send email
    graphics = [summary_barchart, priority_barchart, classification_piechart, team_barchart, unclassified_piechart]
    send_email_from_graphics(graphics, online_bug_source)
