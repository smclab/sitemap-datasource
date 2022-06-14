# Web Parser

This is a parser to crawl and extract web pages and documents from web site using sitemap. \
Run container from built image and configure appropriate plugin to call it.\
This parser is built with the Scrapy library.

You can access the Scrapyd server console via port 6800. By accessing it you can, for each job, monitor its status and view its logs.\
The container takes via environment variable INGESTION_URL, which must match the url of the Ingestion Api.\

## Web Parser Api

This Rest service exposes two different endpoints:

### Execute Sitemap Web Crawler enpoint

Call this endpoint to execute a crawler that extract web pages starting from sitemap or from robots.txt file

This endpoint takes different arguments in JSON raw body:

- **sitemapUrls**: robots.txt file or sitemap list
- **allowedDomains**: username of specific liferay account
- **datasourceId**: id of datasource in Openk9
- **timestamp**: timestamp to check data to be extracted
- **bodyTag**: html tag for main content to extract from page
- **titleTag**: html tag for title to assign to extracted page (optional parameter, if not specified title from title tag is taken)
- **maxLength**: max length in characters for extracted content. If content length exceeds maxLength is truncated.
- **replaceRule**: rule expressed as list of two elements, where first is element to replace and second string with which to replace (optional parameter, if not specified, no replacement is done)

Follows an example of Curl call:

```
curl --location --request POST 'http://localhost:5008/execute-sitemap' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sitemapUrls": ["https://www.smc.it/sitemap.xml"],
    "allowedDomains": ["smc.it"],
    "bodyTag": "div#main-content",
    "titleTag": "title::text",
    "datasourceId": 1,
    "timestamp": 0,
    "maxLength": 10000
}'
```

### Cancel Job endpoint

Call this endpoint to cancel running job before it ends 

This endpoint takes the job_id as url parameter:

- **job_id**: id of running job

Follows an example of Curl call:

```
curl --location --request POST 'http://localhost:5008/cancel-job/{job_id}'
```