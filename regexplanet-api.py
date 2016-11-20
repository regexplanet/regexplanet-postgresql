#!/usr/bin/python
#
# python program to call Postgresql to test regular expressions
#

import cgi
import json
import platform
import re
import sysconfig
import sys
import webapp2

def add_if_exists(obj, key, value):
	if value:
		obj[key] = value

class StatusPage(webapp2.RequestHandler):
	def get(self):

		retVal = {}
		retVal["success"] = True
		retVal["message"] = "OK"
		retVal["version"] = "%s (%s)" % (platform.python_version(), platform.python_implementation())
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

		options = set(self.request.get_all('option'))
		flags = 0
		flagList = []
		if "ignorecase" in options:
			flags |= re.IGNORECASE
			flagList.append("IGNORECASE")
		if "locale" in options:
			flags |= re.LOCALE
			flagList.append("LOCALE")
		if "multiline" in options:
			flags |= re.MULTILINE
			flagList.append("MULTILINE")
		if "dotall" in options:
			flags |= re.DOTALL
			flagList.append("DOTALL")
		if "unicode" in options:
			flags |= re.UNICODE
			flagList.append("UNICODE")
		if "verbose" in options:
			flags |= re.VERBOSE
			flagList.append("VERBOSE")


		html = []
		html.append('<table class="table table-bordered table-striped" style="width:auto;">\n')
		html.append('\t<tbody>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('Regular Expression')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(cgi.escape(regex))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('as a raw Python string')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(cgi.escape("r'" + regex + "'"))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('as a regular Python string (with re.escape())')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(cgi.escape("'" + re.escape(regex)) + "'")
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('replacement')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(cgi.escape(replacement))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		if len(options) > 0:
			html.append('\t\t<tr>\n')
			html.append('\t\t\t<td>')
			html.append('flags (as constants)')
			html.append('</td>\n')
			html.append('\t\t\t<td>')
			html.append(cgi.escape("|".join(flagList)))
			html.append('</td>\n')
			html.append('\t\t</tr>\n')

		try:
			pattern = re.compile(regex, flags)
		except Exception as e:
			html.append('\t\t<tr>\n')
			html.append('\t\t\t<td>')
			html.append('Exception')
			html.append('</td>\n')
			html.append('\t\t\t<td>')
			html.append(cgi.escape(str(e)))
			html.append('</td>\n')
			html.append('\t\t</tr>\n')
			html.append('\t</tbody>\n')
			html.append('</table>\n')
			return json.dumps({"success": False, "message": "re.compile() Exception:" + str(e), "html": "".join(html)})

		if len(options) > 0:
			html.append('\t\t<tr>\n')
			html.append('\t\t\t<td>')
			html.append('flags')
			html.append('</td>\n')
			html.append('\t\t\t<td>')
			html.append(str(pattern.flags))
			html.append('</td>\n')
			html.append('\t\t</tr>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('# of groups (.group)')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(str(pattern.groups))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t\t<tr>\n')
		html.append('\t\t\t<td>')
		html.append('Group name mapping (.groupindex)')
		html.append('</td>\n')
		html.append('\t\t\t<td>')
		html.append(str(pattern.groupindex))
		html.append('</td>\n')
		html.append('\t\t</tr>\n')

		html.append('\t</tbody>\n')
		html.append('</table>\n')

		html.append('<table class="table table-bordered table-striped">\n')
		html.append('\t<thead>\n')
		html.append('\t\t<tr>\n')
		html.append('\t\t\t<th style="text-align:center;">Test</th>\n')
		html.append('\t\t\t<th>Target String</th>\n')
		html.append('\t\t\t<th>findall()</th>\n')
		#html.append('\t\t\t<th>match()</th>\n')
		html.append('\t\t\t<th>split()</th>\n')
		html.append('\t\t\t<th>sub()</th>\n')
		html.append('\t\t\t<th>search()</th>\n')
		for loop in range(0, pattern.groups+1):
			html.append('\t\t\t<th>group(')
			html.append(str(loop))
			html.append(')</th>\n');

		html.append('\t\t</tr>');
		html.append('\t</thead>');
		html.append('\t<tbody>');

		for loop in range(0, len(inputs)):

			test = inputs[loop]

			if len(test) == 0:
				continue

			matcher = pattern.search(test)

			html.append('\t\t<tr>\n')
			html.append('\t\t\t<td style="text-align:center">')
			html.append(str(loop+1))
			html.append('</td>\n')

			html.append('\t\t\t<td>')
			html.append(cgi.escape(test))
			html.append('</td>\n')

			html.append('\t\t\t<td>')
			html.append(cgi.escape(str(pattern.findall(test))))
			html.append('</td>\n')

			#html.append('\t\t\t<td>')
			#html.append(cgi.escape(str(pattern.match(test))))
			#html.append('</td>\n')

			html.append('\t\t\t<td>')
			html.append(cgi.escape(str(pattern.split(test))))
			html.append('</td>\n')

			html.append('\t\t\t<td>')
			html.append(cgi.escape(str(pattern.sub(replacement, test))))
			html.append('</td>\n')

			html.append('\t\t\t<td>')
			if matcher:
				html.append("pos=%d&nbsp;start()=%d&nbsp;end()=%d" % (matcher.pos, matcher.start(), matcher.end()))
			html.append('</td>\n')

			for group in range(0, pattern.groups+1):
				html.append('\t\t\t<td>')
				if matcher:
					html.append(cgi.escape(matcher.group(group)))
				html.append('</td>\n');

			html.append('\t\t</tr>\n')

			while matcher:
				matcher = pattern.search(test, matcher.end())
				if matcher:
					html.append('\t\t<tr>\n');
					html.append('\t\t\t<td colspan="5">&nbsp;</td>\n')
					html.append('\t\t\t<td>')
					html.append("pos=%d&nbsp;start()=%d&nbsp;end()=%d" % (matcher.pos, matcher.start(), matcher.end()))
					html.append('</td>\n')

					for group in range(0, pattern.groups+1):
						html.append('\t\t\t<td>')
						html.append(cgi.escape(matcher.group(group)))
						html.append('</td>\n');

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
	httpserver.serve(app, host='127.0.0.1', port='8080')
