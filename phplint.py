# Copyright (c) 2012 Jan Pecha (http://janpecha.iunas.cz/) All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from gi.repository import GObject, Gtk, Gedit
import re
import subprocess

class PhpLintGlobal:
	windowClass = 0


class PhpLintAfterSavePlugin(GObject.Object, Gedit.ViewActivatable):
	"""Run PHPLint after save document"""

	__gtype_name__ = "PhpLintAfterSavePlugin"
	view = GObject.property(type=Gedit.View)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		"""Activate plugin."""
		self.doc = self.view.get_buffer()
		self.handler_id = self.doc.connect("saved", self.on_document_saving)

	def do_deactivate(self):
		"""Deactivate plugin."""
		self.doc.disconnect(self.handler_id)

	def do_update_state(self):
		"""Window state updated"""
		pass

	def on_document_saving(self, *args):
		"""Strip trailing spaces in document."""
		lang = self.doc.get_language().get_name()
		
		#self.view.select_all()
		
		if lang == "PHP":
			self.run_phplint()

	def run_phplint(self):
		cmdline = 'php -l -f "' + self.doc.get_location().get_path() + '"'
		p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
		output, errors = p.communicate()
		
		if p.returncode:
			pos = errors.find('on line')
			
			if pos != -1:
				# extract error message
				errorMsg = errors[0:(pos-1)].strip()
				
				# extract line number
				pos = pos + 8
				lineNum = ""
				errors = errors[pos:]
				
				for letter in errors:
					if letter.isdigit():
						lineNum += letter
					else:
						break
				
				lineNum = int(float(lineNum))
				
				# select error line
				self.doc.goto_line(lineNum)
				self.view.scroll_to_cursor()
				if PhpLintGlobal.windowClass != 0:
					PhpLintGlobal.windowClass.setPanelErrorMessage(errorMsg)
		else:
			if PhpLintGlobal.windowClass != 0:
				PhpLintGlobal.windowClass.setPanelNoErrors()

class PhpLintAfterSaveWindowPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "PhpLintAfterSaveWindowPlugin"
	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		icon = Gtk.Image.new_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.MENU)
		self._bottom_widget = Gtk.Label("No errors.")
		panel = self.window.get_bottom_panel()
		panel.add_item(self._bottom_widget, "PhpLintAfterSaveBottomPanel", "PHP Errors", icon)
		panel.activate_item(self._bottom_widget)
		
		PhpLintGlobal.windowClass = self

	def do_deactivate(self):
		panel = self.window.get_bottom_panel()
		panel.remove_item(self._bottom_widget)

	def do_update_state(self):
		pass

	def setPanelErrorMessage(self, msg):
		panel = self.window.get_bottom_panel()
		self._bottom_widget.set_text(msg)
		panel.activate_item(self._bottom_widget)
		panel.show()

	def setPanelNoErrors(self):
		self._bottom_widget.set_text('No errors.')
		# TODO: panel.hide()

