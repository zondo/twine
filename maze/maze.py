"""
Create maze rooms for import to Twine.
"""

import os
import sys
import yaml
import textwrap


imagedir = "images"


def main(args=sys.argv[1:]):
    if len(args) == 1:
        configfile = args[0]
        with open(configfile) as fp:
            data = yaml.safe_load(fp)

        write_twine_rooms(data)
    else:
        sys.exit("usage: %s CONFIGFILE" % sys.argv[0])


def write_twine_rooms(data, roomdir="mazerooms"):
    rooms = data["rooms"]
    types = {int(r["number"]): r["type"] for r in rooms}

    if not os.path.exists(roomdir):
        os.makedirs(roomdir)

    path = os.path.join(roomdir, "init.txt")
    with open(path, "w") as fp:
        for line in startup():
            fp.write(line + "\n")

    for room in rooms:
        filename = "room-%02d.txt" % int(room["number"])
        path = os.path.join(roomdir, filename)
        with open(path, "w") as fp:
            for line in room_text(room, types):
                fp.write(line + "\n")


def room_text(room, types):
    yield "$intro[" + room["intro"] + "]"
    yield ""

    for line in image_ref(room):
        yield line

    for line in room_desc(room):
        yield line

    for line in twine_links(room, types):
        yield line

    num = int(room["number"])
    links = room.get("links", [])

    if links:
        yield "{"

        for line in javascript(links):
            yield line

        for line in image_map(num, links):
            yield line

        yield "}"


def startup():
    yield "{"
    yield '\t(set: $imagedir to "%s")' % imagedir
    yield '\t(set: $intro to (text-style: "bold"))'
    yield "}"


def room_desc(room):
    paras = room["text"].split("\n\n")
    for para in paras:
        yield textwrap.fill(para, width=1000)
        yield ""


def image_ref(room):
    num = int(room["number"])

    yield "{"
    yield "\t(set: _img to 'img src=\"' + $imagedir + '/room-%02d.jpg\"')" % num
    yield "\t(set: _img to it + ' title=\"Room %d\"')" % num
    yield "\t(set: _img to it + ' usemap=\"#room-%02d\"')" % num
    yield "\t(set: _img to '<' + _img + '>')"
    yield "\t(set: _img to '<center>' + _img + '</center>')"
    yield "\t(print: _img)"
    yield "}"


def twine_links(room, types):
    rtype = room["type"]
    links = room.get("links", [])

    for link in links:
        onum = int(link["dir"])
        otype = types[onum]

        if rtype == otype:
            yield "[[...room %d->%02d]]" % (onum, onum)
        else:
            yield '[(link-goto: "...room %d", "%02d")]' % (onum, onum)


def javascript(links):
    yield "<script>"

    for link in links:
        onum = int(link["dir"])

        yield '$(\'area[alt="%02d"]\').on("click", function(e){' % onum
        yield "\te.preventDefault();"
        yield "\t$(\"tw-link[passage-name='%02d']\").click();" % onum
        yield "});"

    yield "</script>"


def image_map(num, links):
    yield '<map name="room-%02d">' % num

    for link in links:
        poly = link["map"]
        onum = int(link["dir"])
        yield '<area shape="poly" coords="%s" alt="%02d">' % (poly, onum)

    yield "</map>"


if __name__ == "__main__":
    main()
