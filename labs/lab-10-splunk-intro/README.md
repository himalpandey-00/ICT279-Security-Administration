# Lab 10 – Splunk Introduction

## Overview

This lab introduced Splunk Enterprise and its basic data analysis and search capabilities. The lab used the Splunk Search & Reporting application with the `tutorialdata.zip` dataset containing web access logs, secure logs, and sales-related data from the fictional Buttercup Games environment.

The main activities completed in this lab included:

- Installing and accessing Splunk Enterprise
- Uploading and indexing the tutorial dataset
- Exploring events using the time picker and event timeline
- Searching data using Splunk Search Processing Language (SPL)
- Working with extracted fields
- Searching successful and failed transactions
- Using Boolean operators and wildcards
- Using transforming commands such as `top`, `stats`, and `chart`
- Creating visualisations
- Using subsearches to correlate results
- Creating a report
- Creating a dashboard

---

## Environment

| Component | Details |
|---|---|
| Platform | Splunk Enterprise |
| Host OS | Windows 10 VM |
| Interface | Splunk Web |
| Dataset | `tutorialdata.zip` |
| Splunk Application | Search & Reporting |
| Dataset Scenario | Buttercup Games |

---

# 1. Splunk Enterprise Setup

Splunk Enterprise was installed on the Windows 10 virtual machine and accessed through the Splunk Web interface.

![Splunk Enterprise Home](screenshots/01-splunk-enterprise-home.png)

---

# 2. Uploading and Indexing the Tutorial Data

The `tutorialdata.zip` dataset was uploaded through:

**Settings → Add Data → Upload**

The source type was left on automatic detection.

For the host configuration, **Segment in path** was selected with:

```text
Segment number: 1
```

This allows Splunk to determine host information from the path structure of the files contained in the archive.

![Splunk Input Settings](screenshots/02-splunk-input-settings.png)

The configuration was reviewed before importing the data.

![Tutorial Data Review](screenshots/03-tutorial-data-review.png)

Splunk successfully uploaded and indexed the dataset.

![Tutorial Data Upload Success](screenshots/04-tutorial-data-upload-success.png)

---

# 3. Exploring the Dataset

The `www1/access.log` source was selected to explore Apache web access events.

![WWW1 Access Log Search](screenshots/05-www1-access-log-search.png)

Splunk automatically extracted useful information from the events including fields such as:

- `host`
- `source`
- `sourcetype`
- `clientip`
- `status`
- `action`
- `categoryId`
- `productId`

## Time Range Investigation

The time picker was used to restrict the search to the final day of the dataset.

![Last Day Time Range](screenshots/06-last-day-time-range.png)

The event timeline was then used to select a one-hour period and investigate events occurring during that interval.

![One Hour Timeline Selection](screenshots/07-one-hour-timeline-selection.png)

This demonstrated how Splunk can narrow an investigation to a particular period of interest.

---

# 4. Basic SPL Searches

## Error and Failure Search

The following search was used to identify events containing errors, failures, or severe messages:

```spl
buttercupgames (error OR fail* OR severe)
```

The search demonstrates:

- Boolean `OR`
- Parentheses for grouping
- `*` as a wildcard

![Error and Failure Search](screenshots/08-error-failure-search.png)

---

# 5. Working with Fields

Web access events were retrieved using:

```spl
sourcetype=access_*
```

Splunk extracted structured fields from the raw Apache log data. The following fields were selected for easier analysis:

```text
action
categoryId
productId
```

![Selected Fields Table](screenshots/09-selected-fields-table.png)

These fields make it possible to perform more targeted searches without manually analysing the complete raw log entry.

---

# 6. Successful and Failed Purchases

## Successful Purchases

Successful purchase events were searched using:

```spl
sourcetype=access_* status=200 action=purchase
```

`status=200` identifies successful HTTP requests while `action=purchase` limits the results to purchase events.

![Successful Purchases](screenshots/10-successful-purchases.png)

## Failed Purchases

Failed or unsuccessful purchase requests were identified using:

```spl
sourcetype=access_* status!=200 action=purchase
```

The `!=` operator excludes HTTP status 200.

The results included HTTP error responses such as 404, 500 and 503.

![Failed Purchases](screenshots/11-failed-purchases.png)

---

# 7. Searching Across Multiple Log Sources

A broader error search was performed using:

```spl
(error OR fail* OR severe) OR (status=404 OR status=500 OR status=503)
```

Unlike the earlier web-only searches, this query does not restrict the search to a particular source type.

The results therefore included multiple sources such as:

- `www1/secure.log`
- `www2/secure.log`
- `www3/secure.log`
- `mailsv/secure.log`
- Web access logs

![Error Search Across Multiple Sources](screenshots/12-error-search-multiple-sources.png)

This demonstrates how Splunk can search and correlate information across different log sources.

---

# 8. Transforming Searches with `top`

Splunk's `top` command was used to identify frequently occurring values.

## Most Popular TEE Product – All Time

The following search identified the most frequently purchased product in the TEE category:

```spl
sourcetype=access_* status=200 action=purchase categoryId=TEE
| top productId
```

Results:

| Product ID | Count | Percentage |
|---|---:|---:|
| `MB-AG-T01` | 206 | 56.13% |
| `WC-SH-T02` | 161 | 43.87% |

The most popular TEE product was therefore:

```text
MB-AG-T01
```

![Top TEE Product All Time](screenshots/13-top-tee-product-all-time.png)

## First 24 Hours

The same search was restricted to the first 24 hours of the dataset.

Results:

| Product ID | Count | Percentage |
|---|---:|---:|
| `MB-AG-T01` | 28 | 57.14% |
| `WC-SH-T02` | 21 | 42.86% |

`MB-AG-T01` remained the most popular TEE product during the first 24 hours.

![Top TEE Product First 24 Hours](screenshots/14-top-tee-product-first-24-hours.png)

---

# 9. Category Analysis and Visualisation

The following search ranked successful purchases by product category:

```spl
sourcetype=access_* status=200 action=purchase
| top categoryId
```

Seven categories were returned:

| Category | Count |
|---|---:|
| STRATEGY | 806 |
| ARCADE | 493 |
| TEE | 367 |
| ACCESSORIES | 348 |
| SIMULATION | 246 |
| SHOOTER | 245 |
| SPORTS | 138 |

The results were displayed using a pie chart.

![Category Purchases Pie Chart](screenshots/15-category-purchases-pie-chart.png)

The TEE product IDs were also visualised using:

```spl
sourcetype=access_* status=200 action=purchase categoryId=TEE
| top productId
```

![TEE Product Pie Chart](screenshots/16-tee-product-pie-chart.png)

---

# 10. VIP Shopper Analysis

The most frequent shopper was identified using:

```spl
sourcetype=access_* status=200 action=purchase
| top limit=1 clientip
```

The most frequent customer was:

```text
87.194.216.51
```

Further analysis was performed using:

```spl
sourcetype=access_* status=200 action=purchase clientip=87.194.216.51
| stats count, distinct_count(productId), values(productId) by clientip
```

The results showed:

| Metric | Result |
|---|---:|
| VIP Customer | `87.194.216.51` |
| Total Purchases | 134 |
| Distinct Products | 14 |

![VIP Shopper Statistics](screenshots/17-vip-shopper-stats.png)

---

# 11. Using a Subsearch

Instead of manually identifying the VIP customer's IP address first, a subsearch was used to dynamically determine the most frequent shopper.

```spl
sourcetype=access_* status=200 action=purchase
[search sourcetype=access_* status=200 action=purchase
| top limit=1 clientip
| table clientip]
| stats count AS "Total Purchased",
        distinct_count(productId) AS "Total Products",
        values(productId) AS "Product IDs" by clientip
| rename clientip AS "VIP Customer"
```

The search inside the square brackets is processed first and returns the top `clientip`. The outer search then analyses purchases made by that customer.

The output fields were renamed to make the results easier to understand.

![VIP Subsearch Renamed Fields](screenshots/18-vip-subsearch-renamed-fields.png)

---

# 12. Creating a Report

The VIP customer search was saved as a Splunk report.

**Report title:**

```text
VIP Customer
```

**Description:**

```text
Buttercup Games most frequent shopper
```

The report retained the time range picker so that the analysis can be executed against different periods.

![VIP Customer Report](screenshots/19-vip-customer-report.png)

---

# 13. Creating a Dashboard

The final task was to analyse purchases made by the four most frequent customers.

The following SPL search was used:

```spl
sourcetype=access_* status=200 action=purchase categoryId!=""
[search sourcetype=access_* status=200 action=purchase categoryId!=""
| top limit=4 clientip
| table clientip]
| chart count by clientip, productId
```

The subsearch dynamically identifies the four most frequent customers. The `chart` command then counts product purchases for each customer.

The result was saved as a dashboard containing a pie-chart visualisation.

**Dashboard:** `VIP Purchase`

**Panel:** `Products`

![VIP Purchases Dashboard](screenshots/20-vip-purchases-dashboard.png)

---

# Key SPL Commands Used

| Command / Operator | Purpose |
|---|---|
| `sourcetype=` | Restrict events by source type |
| `status=200` | Match successful HTTP responses |
| `status!=200` | Match non-successful HTTP responses |
| `OR` | Match alternative conditions |
| `*` | Wildcard matching |
| `\|` | Pass results to another SPL command |
| `top` | Find the most frequent field values |
| `limit=1` | Restrict `top` to one result |
| `stats` | Calculate statistics from events |
| `count` | Count matching events |
| `distinct_count()` | Count unique field values |
| `values()` | Return unique values of a field |
| `table` | Display selected fields |
| `chart` | Produce structured results for visualisation |
| `AS` | Assign a readable alias |
| `rename` | Rename an output field |
| `[search ...]` | Execute a subsearch before the outer search |

---

# Key Findings

- Splunk successfully indexed and searched multiple log types from the Buttercup Games dataset.
- Time ranges and the event timeline can significantly narrow an investigation.
- Extracted fields allow targeted searches without manually parsing raw log entries.
- HTTP status codes can be used to distinguish successful and unsuccessful requests.
- A single SPL search can search across multiple log sources.
- `top`, `stats`, and `chart` transform raw events into useful analytical results.
- `MB-AG-T01` was the most popular TEE product across both the whole dataset and the first 24 hours.
- `87.194.216.51` was the most frequent shopper in the analysed dataset.
- The VIP shopper generated 134 successful purchase events involving 14 distinct products.
- Subsearches can dynamically feed results into another search, avoiding manually entered intermediate values.
- Splunk search results can be converted into reusable reports and dashboards.

---

# Conclusion

This lab provided practical experience with the main Splunk workflow: ingesting machine data, indexing it, searching events with SPL, analysing structured fields, transforming results, and presenting findings through reports and dashboards.

The exercises also demonstrated how Splunk can combine events from different log sources and use time ranges, HTTP status codes, extracted fields, statistical commands and subsearches to investigate activity within a dataset.

These techniques provide a foundation for using Splunk for security monitoring, threat detection, incident investigation and log analysis in later security-focused exercises.