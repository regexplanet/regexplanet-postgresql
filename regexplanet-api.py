#!/usr/bin/python
#
# python program to call Postgresql to test regular expressions
#

import cgi
import datetime
import json
import os
import platform
import psycopg2
import re
import sysconfig
import sys
import urlparse
import uuid
import webapp2

def safe_escape(target):
	if target is None:
		return "<i>(null)</i>"

	if len(target) == 0:
		return "<i>(empty)</i>"

	return cgi.escape(target)

def pg_connect():
    urlparse.uses_netloc.append("postgres")

    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    return conn

def pg_escape(s):
   if not isinstance(s, basestring):
       raise TypeError("%r must be a str or unicode" %(s, ))
   escaped = repr(s)
   if isinstance(s, unicode):
       assert escaped[:1] == 'u'
       escaped = escaped[1:]
   if escaped[:1] == '"':
       escaped = escaped.replace("'", "\\'")
   elif escaped[:1] != "'":
       raise AssertionError("unexpected repr: %s", escaped)
   return "E'%s'" %(escaped[1:-1], )

def do_query(query, params):

    cols = []
    rows = []

    #t = Template(raw_query)
    #query = t.render(metadata["params"])

    conn = pg_connect()
    cur = conn.cursor()
    cur.execute(query)

    for col_metadata in cur.description:
        cols.append(col_metadata[0])

    for row in cur:
        rows.append(row)


    conn.close()

    return cols, rows

def add_if_exists(obj, key, value):
	if value:
		obj[key] = value

class StatusPage(webapp2.RequestHandler):
	def get(self):

		retVal = {}
		retVal["success"] = True
		retVal["message"] = "OK"

		add_if_exists(retVal, "platform.machine()", platform.machine())
		add_if_exists(retVal, "platform.node()", platform.node())
		#IOError: add_if_exists(retVal, "platform.platform()", platform.platform())
		add_if_exists(retVal, "platform.processor()", platform.processor())
		add_if_exists(retVal, "platform.python_branch()", platform.python_branch())
		add_if_exists(retVal, "platform.python_build()", platform.python_build())
		add_if_exists(retVal, "platform.python_compiler()", platform.python_compiler())
		add_if_exists(retVal, "platform.python_implementation()", platform.python_implementation())
		add_if_exists(retVal, "platform.python_version()", platform.python_version())
		add_if_exists(retVal, "platform.python_revision()", platform.python_revision())
		add_if_exists(retVal, "platform.release()", platform.release())
		add_if_exists(retVal, "platform.system()", platform.system())
		add_if_exists(retVal, "platform.version()", platform.version())
		add_if_exists(retVal, "platform.uname()", platform.uname())
		add_if_exists(retVal, "sysconfig.get_platform()", sysconfig.get_platform())
		add_if_exists(retVal, "sysconfig.get_python_version()", sysconfig.get_python_version())
		add_if_exists(retVal, "sys.byteorder", sys.byteorder)
		add_if_exists(retVal, "sys.copyright", sys.copyright)
		add_if_exists(retVal, "sys.getdefaultencoding()", sys.getdefaultencoding())
		add_if_exists(retVal, "sys.getfilesystemencoding()", sys.getfilesystemencoding())
		add_if_exists(retVal, "sys.maxint", sys.maxint)
		add_if_exists(retVal, "sys.maxsize", sys.maxsize)
		add_if_exists(retVal, "sys.maxunicode", sys.maxunicode)
		add_if_exists(retVal, "sys.version", sys.version)
		
		if "DATABASE_URL" in os.environ:

		    cols, rows = do_query("SELECT version(), current_setting('server_version'), current_setting('server_version_num');", None)
		    dbdetail = rows[0][0] if len(rows) > 0 else None
		    dbversion = rows[0][1] if len(rows) > 0 else None
		    dbversionnum = rows[0][2] if len(rows) > 0 else None
		    retVal["version"] = dbversion

		    add_if_exists(retVal, "SELECT version();", dbdetail)
		    add_if_exists(retVal, "SELECT current_setting('server_version_num');", dbversionnum)
		else:
		    add_if_exists(retVal, "Database", "NOT CONFIGURED")

		self.response.headers['Content-Type'] = 'text/plain'

		callback = self.request.get('callback')
		if len(callback) == 0 or re.match("[a-zA-Z][-a-zA-Z0-9_]*$", callback) is None:
			self.response.out.write(json.dumps(retVal, separators=(',', ':')))
		else:
			self.response.out.write(callback)
			self.response.out.write("(")
			self.response.out.write(json.dumps(retVal, separators=(',', ':')))
			self.response.out.write(");")

	def post(self):
		self.get()

class TestPage(webapp2.RequestHandler):
	def get(self):

		retVal = self.doTest()

		self.response.headers['Content-Type'] = 'text/plain'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'
		self.response.headers['Access-Control-Max-Age'] = '604800' # 1 week

		callback = self.request.get('callback')
		if len(callback) == 0 or re.match("[a-zA-Z][-a-zA-Z0-9_]*$", callback) is None:
			self.response.out.write(retVal)
		else:
			self.response.out.write(callback)
			self.response.out.write("(")
			self.response.out.write(retVal)
			self.response.out.write(");")

	def options(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'
		self.response.headers['Access-Control-Max-Age'] = '604800' # 1 week
		self.response.out.write('Yes, CORS is allowed!')

	def post(self):
		self.get()

	def doTest(self):

		regex = self.request.get('regex')
		if len(regex) == 0:
			return json.dumps({"success": False, "message": "no regular expression to test"})

		replacement = self.request.get('replacement')
		inputs = self.request.get_all('input')
		if len(inputs) == 0:
			return json.dumps({"success": False, "message": "no input for test the regular expression"})

		html = []
		html.append('<table class="table table-bordered table-striped" style="width:auto;">\n')
		html.append('\t<tbody>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('Regular Expression')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(safe_escape(regex))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('replacement')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(safe_escape(replacement))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t</tbody>\n')
		html.append('</table>\n')

		conn = pg_connect()
		cur = conn.cursor()
		# create the table
		tablename = "test_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S") + "_" + str(uuid.uuid4()).replace('-', '')
		cur.execute("CREATE UNLOGGED TABLE %(table)s (LIKE template);", {"table": psycopg2.extensions.AsIs(tablename) })
		conn.commit()

		# add the inputs
		for loop in range(0, len(inputs)):

			test = inputs[loop]

			if len(test) == 0:
				continue

			cur.execute("INSERT INTO %(table)s (id, input, regex, replacement) VALUES(%(id)s, %(input)s, %(regex)s, %(replacement)s)", {"id": loop, "table": psycopg2.extensions.AsIs(tablename), "input": test, "regex": regex, "replacement": replacement})

		conn.commit()

		cur.execute("SELECT (id+1)::varchar, input, (input SIMILAR TO regex)::varchar, (input ~ regex)::varchar, (input ~* regex)::varchar, (input !~ regex)::varchar, (input !~* regex)::varchar, substring(input from regex), regexp_replace(input, regex, replacement) FROM %(table)s", { "table": psycopg2.extensions.AsIs(tablename) })

		rows = []
		for row in cur:
			rows.append(row)

		matches = {}
		cur.execute("SELECT (id+1)::varchar, UNNEST(regexp_matches(input, regex)) FROM %(table)s", { "table": psycopg2.extensions.AsIs(tablename) })
		for row in cur:
			if row[0] in matches:
				matches[row[0]].append(row[1])
			else:
				matches[row[0]] = [ row[1] ]

		cur.execute("DROP TABLE %(table)s;", { "table": psycopg2.extensions.AsIs(tablename) })
		conn.commit()

		conn.close()

		html.append('<table class="table table-bordered table-striped">\n')
		html.append('\t<thead>\n')
		html.append('\t\t<tr>\n')
		html.append('\t\t\t<th style="text-align:center;">Test</th>\n')
		html.append('\t\t\t<th>Target String</th>\n')
		html.append('\t\t\t<th>SIMILAR TO</th>\n')
		html.append('\t\t\t<th>~</th>\n')
		html.append('\t\t\t<th>~*</th>\n')
		html.append('\t\t\t<th>!~</th>\n')
		html.append('\t\t\t<th>!~*</th>\n')
		html.append('\t\t\t<th>substring()</th>\n')
		html.append('\t\t\t<th>regex_replace()</th>\n')
		html.append('\t\t\t<th>regex_matches()</th>\n')
		html.append('\t\t</tr>');
		html.append('\t</thead>');
		html.append('\t<tbody>');

		for row in rows:

			html.append('\t\t<tr>\n')
			html.append('\t\t\t<td style="text-align:center">')
			html.append(cgi.escape(row[0]))
			html.append('</td>\n')

			for col in range(1,9):
				html.append('\t\t\t<td>')
				html.append(safe_escape(row[col]))
				html.append('</td>\n')

			html.append('\t\t\t<td>')
			if row[0] not in matches:
				html.append("<i>(none)</i>")
			else:
				matchlist = matches[row[0]]
				for matchloop in range(0, len(matchlist)):
					html.append("%d: %s<br/>" % (matchloop+1, safe_escape(matchlist[matchloop])))
			html.append('</td>\n')

			html.append('\t\t</tr>\n')


		html.append('\t</tbody>\n')
		html.append('</table>\n')

		return json.dumps({"success": True, "html": "".join(html)})

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Location'] = 'http://www.regexplanet.com/advanced/python/index.html'
		self.response.status = 307

app = webapp2.WSGIApplication(	[
									('/', MainPage),
									('/status.json', StatusPage),
									('/test.json', TestPage)
								],
								debug=True)


if __name__ == '__main__':
	from paste import httpserver
	httpserver.serve(app, host='0.0.0.0', port='8080')
