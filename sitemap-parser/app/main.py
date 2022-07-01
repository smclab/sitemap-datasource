"""
Copyright (c) 2020-present SMC Treviso s.r.l. All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
import logging
import os
import requests
import json

app = FastAPI()

ingestion_url = os.environ.get("INGESTION_URL")
if ingestion_url is None:
    ingestion_url = "http://ingestion:8080/v1/ingestion/"

log_level = os.environ.get("INPUT_LOG_LEVEL")
if log_level is None:
    log_level = "INFO"

logger = logging.getLogger(__name__)


class SitemapRequest(BaseModel):
    sitemapUrls: list
    bodyTag: str
    titleTag: Optional[str] = "title::text"
    datasourceId: int
    scheduleId: str
    timestamp: int
    replaceRule: Optional[list] = ["", ""]
    allowedDomains: list
    maxLength: Optional[int] = None


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def post_message(url, payload, timeout=30):
    try:
        r = requests.post(url, data=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()
    except requests.RequestException as e:
        logger.error(str(e) + " during request at url: " + str(url))
        raise e


@app.post("/execute-sitemap")
def execute(request: SitemapRequest):

    request = request.dict()

    sitemap_urls = request['sitemapUrls']
    body_tag = request["bodyTag"]
    title_tag = request["titleTag"]
    datasource_id = request['datasourceId']
    schedule_id = request['scheduleId']
    timestamp = request["timestamp"]
    allowed_domains = request["allowedDomains"]
    max_length = request["maxLength"]
    replace_rule = request["replaceRule"]

    payload = {
        "project": "sitemap",
        "spider": "CustomSitemapSpider",
        "sitemap_urls": json.dumps(sitemap_urls),
        "allowed_domains": json.dumps(allowed_domains),
        "body_tag": body_tag,
        "title_tag": title_tag,
        "replace_rule": json.dumps(replace_rule),
        "datasource_id": datasource_id,
        "schedule_id": schedule_id,
        "ingestion_url": ingestion_url,
        "timestamp": timestamp,
        "max_length": max_length,
        "setting": ["LOG_LEVEL=%s" % log_level]
    }

    response = post_message("http://localhost:6800/schedule.json", payload)

    if response["status"] == 'ok':
        logger.info("Crawling process started")
        return "Crawling process started with job " + str(response["jobid"])
    else:
        return response


@app.post("/cancel-job/{job_id}")
def cancel_job(job_id: str):

    payload = {
        "project": "sitemap",
        "job": str(job_id)
    }

    response = post_message("http://localhost:6800/cancel.json", payload, 10)

    if response["status"] == 'ok':
        return "Cancelled job with id " + str(job_id)
    else:
        return response


