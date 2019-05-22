#!/usr/bin/env python
# -*- coding: utf-8 -*-

import emoji
from jinja2 import Template
import sys
from dateutil.parser import parse


def get_tstamp(date, hour):
    return parse("%s %s" % (date, hour), dayfirst=True)


def get_smileys(dataline):
    # import pdb; pdb.set_trace()
    return [c for c in dataline if c in emoji.UNICODE_EMOJI]


def data_form_line(line):
    if " " in line and "/" in line and " - " in line:
        dataline = line.split(" ")
        if len(dataline) < 5:
            return
        if dataline[1] != u"à":
            return
        date, _, hour, _, firstname = dataline[:5]
        if firstname.endswith(":"):
            firstname = firstname[:-1]
        return get_tstamp(date, hour), firstname, get_smileys(line)


def get_datas(filename, limit=None):
    with open(filename, "r") as fp:
        data = fp.readlines()
    linedata = None
    datas = []
    if limit:
        data = data[:limit]
    for line in data:
        line = line.strip().decode("utf8")
        newdata = data_form_line(line)
        if newdata is None:
            newdata = linedata
        datas.append(newdata)
        linedata = newdata
    return datas


def do_html():
    datas = get_datas(sys.argv[1], limit=20000)
    hashed = {
        "months": {},
        "firstname": {},
        "words": [],
    }
    with open("wamoji.html", "r") as fp:
        template_string = fp.read()
    template = Template(template_string)
    result = []
    for line in datas:
        date, firstname, smileys = line
        month = date.strftime("%Y-%m")
        hashed["months"].setdefault(month, {}).setdefault(firstname, {})
        hashed["firstname"].setdefault(firstname, []).append(line)
        if smileys:
            for smiley in smileys:
                hashed["months"][month][firstname].setdefault(smiley, 0)
                hashed["months"][month][firstname][smiley] += 1
    max_total = 0
    for month in sorted(hashed["months"].keys()):
        month_data = hashed["months"][month]
        mresult = {
            "month": month,
            "data": [],
        }
        for firstname in sorted(month_data.keys()):
            smileys = month_data[firstname]
            fresult = {
                "firstname": firstname,
                "total": float(sum(smileys.values())),
                "data": [],
            }
            max_total = max([max_total, fresult["total"]])
            for smiley, count in sorted(
                smileys.items(),
                key=lambda tup: tup[1],
                reverse=True,
            )[:5]:
                fresult["data"].append({"smiley": smiley, "count": count})
            mresult["data"].append(fresult)
        result.append(mresult)
    return template.render(data=result, ymax=max_total)


def main():
    print(do_html().encode("utf8"))


if __name__ == "__main__":
    main()
