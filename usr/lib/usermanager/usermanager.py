#! /usr/bin/env python3

# Password settings
# http://docs.python.org/2/library/spwd.html#module-spwd
# User settings
# http://docs.python.org/2/library/pwd.html

# Make sure the right Gtk version is loaded
import gi
gi.require_version('Gtk', '3.0')

# sudo apt-get install python3-gi
# from gi.repository import Gtk, GdkPixbuf, GObject, Pango, Gdk
from gi.repository import Gtk, Gdk
#import sys
import os
import functions
from datetime import datetime
# abspath, dirname, join, expanduser, exists, basename
from os.path import join, abspath, dirname, exists
from shutil import move
from execcmd import ExecCmd
from treeview import TreeViewHandler
from combobox import ComboBoxHandler
from dialogs import MessageDialogSave, QuestionDialog, SelectDirectoryDialog, SelectImageDialog
from image import ImageHandler
from user import User

# i18n: http://docs.python.org/3/library/gettext.html
import gettext
from gettext import gettext as _
gettext.textdomain('usermanager')


#class for the main window
class UserManager(object):

    def __init__(self):
        self.scriptDir = abspath(dirname(__file__))

        # Load window and widgets
        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(self.scriptDir, '../../share/usermanager/usermanager.glade'))
        # Main window objects
        go = self.builder.get_object
        self.window = go('usermanagerWindow')
        self.tvUsersMain = go('tvUsersMain')
        self.tvUserGroupsMain = go('tvUserGroupsMain')
        self.chkShowSystemUsers = go('chkShowSystemUsers')
        self.btnUserEdit = go('btnUserEdit')
        self.btnUserRemove = go('btnUserRemove')
        # User window objects
        self.windowUser = go('usermanagerUserWindow')
        self.nbUser = go('nbUser')
        self.txtLoginName = go('txtLoginName')
        self.txtRealName = go('txtRealName')
        self.txtUserID = go('txtUserID')
        self.txtHomeDirectory = go('txtHomeDirectory')
        self.cmbShells = go('cmbShells')
        self.cmbPrimaryGroup = go('cmbPrimaryGroup')
        self.cmbPrimaryGroupEntry = go('cmbPrimaryGroupEntry')
        self.tvUserGroups = go('tvUserGroups')
        self.ebFace = go('ebFace')
        self.imgFace = go('imgFace')
        self.lblUserID = go('lblUserID')
        self.txtPassword = go('txtPassword')
        self.txtLastChanged = go('txtLastChanged')
        self.cmbValidUntilMonth = go('cmbValidUntilMonth')
        self.spbValidUntilDay = go('spbValidUntilDay')
        self.spbValidUntilYear = go('spbValidUntilYear')
        self.radEnabled = go('radEnabled')
        self.radDisabled = go('radDisabled')
        self.radValidUntilAlways = go('radValidUntilAlways')
        self.radValidUntilDate = go('radValidUntilDate')
        self.spbRequirePasswordAfter = go('spbRequirePasswordAfter')
        self.spbWarnBeforePasswordExpires = go('spbWarnBeforePasswordExpires')
        self.spbDisableAccountWhenPasswordExpires = go('spbDisableAccountWhenPasswordExpires')
        self.spbEnforceMinimumPasswordAge = go('spbEnforceMinimumPasswordAge')
        self.chkRequirePasswordAfter = go('chkRequirePasswordAfter')
        self.chkEnforceMinimumPasswordAge = go('chkEnforceMinimumPasswordAge')
        self.tvGroupsMain = go('tvGroupsMain')
        # Group window objects
        self.windowGroup = go('usermanagerGroupWindow')
        self.txtGroupName = go('txtGroupName')
        self.txtGroupID = go('txtGroupID')
        self.tvAccounts = go('tvAccounts')
        self.tvSelectedAccounts = go('tvSelectedAccounts')
        self.tvGroupAccounts = go('tvGroupAccounts')

        # Main window translations
        self.window.set_title(_("User manager"))
        self.chkShowSystemUsers.set_label(_("Show system users"))
        self.btnUserEdit.set_label(_("Edit"))
        self.btnUserRemove.set_label(_("Remove"))
        go('btnUserAdd').set_label(_("Add"))
        go('lblUsersTab').set_text(_("Users"))
        go('lblGroupsTab').set_text(_("Groups"))
        go('lblUsersMain').set_text(go('lblUsersTab').get_text())
        go('lblUserGroupsMain').set_text(_("User groups"))
        go('lblGroupsMain').set_text(go('lblGroupsTab').get_text())
        go('lblGroupAccountsMain').set_text(_("Group accounts"))
        # User window translations
        self.windowUser.set_title(_("User settings"))
        go('lblUserDetails').set_text(_("Details"))
        go('lblStatus').set_text(_("Status"))
        go('lblLoginName').set_text(_("Login name"))
        go('lblRealName').set_text(_("Real name"))
        go('lblUserID').set_text(_("User ID"))
        go('lblPrimaryGroup').set_text(_("Primary group"))
        go('lblHomeDirectory').set_text(_("Home directory"))
        go('lblShell').set_text(_("Shell"))
        self.radEnabled.set_label(_("Enabled"))
        self.radDisabled.set_label(_("Disabled"))
        #go('lblPrivilegesAndGroups').set_text(_("Privileges and groups"))
        go('lblPrivilegesAndGroups').set_text(go('lblGroupsTab').get_text())
        go('lblPrivileges').set_text(_("Privileges"))
        go('lblUserGroups').set_text(go('lblGroupsTab').get_text())
        go('lblPasswordSecurity').set_text(_("Password"))
        go('lblPassword').set_text(go('lblPasswordSecurity').get_text())
        go('lblLastChanged').set_text(_("Last changed"))
        go('lblValidUntil').set_text(_("Valid until"))
        self.radValidUntilAlways.set_label(_("Always"))
        go('lblPasswordAging').set_text(_("Password aging"))
        self.chkRequirePasswordAfter.set_label(_("Require password after"))
        go('lblWarnBeforePasswordExpires').set_text(_("Warn before password expires after"))
        go('lblDisableAccountWhenPasswordExpires').set_text(_("Disable account when password expires after"))
        self.chkEnforceMinimumPasswordAge.set_label(_("Enforce minimum password age"))
        go('lblDays1').set_text(_("days"))
        go('lblDays2').set_text(go('lblDays1').get_text())
        go('lblDays3').set_text(go('lblDays1').get_text())
        go('lblDays4').set_text(go('lblDays1').get_text())
        go('btnSaveUser').set_label(_("Save"))
        go('btnCancelUser').set_label(_("Cancel"))
        # Group window translations
        self.windowGroup.set_title(_("Group settings"))
        go('lblGroupName').set_text(_("Group name"))
        go('lblGroupID').set_text(_("Group ID"))
        go('lblAccounts').set_text(_("Available accounts"))
        go('lblSelectedAccounts').set_text(_("Selected accounts"))
        go('btnOkGroup').set_label(go('btnSaveUser').get_label())
        go('btnCancelGroup').set_label(go('btnCancelUser').get_label())
        go('btnAddAccount').set_label(go('btnUserAdd').get_label())
        go('btnRemoveAccount').set_label(self.btnUserRemove.get_label())

        # Init
        self.ec = ExecCmd()
        self.usr = User()
        self.usersInfo = {}
        self.user = {}
        self.users = []
        self.accounts = []
        self.shells = self.usr.getShells()
        self.groups = None
        self.loggedinUser = self.usr.getLoggedinUser()
        self.loggedinUserPrimaryGroup = self.usr.getUserPrimaryGroupName(self.loggedinUser)
        self.selectedUser = None
        self.selectedGroup = None
        self.selectedGroupAccounts = None
        self.userFace = None
        self.radEnabled.set_active(True)
        self.radValidUntilAlways.set_active(True)
        self.setValidUntil(False)
        self.setRequirePasswordAfter(False)
        self.setEnforceMinimumPasswordAge(False)
        self.txtUserID.set_editable(False)
        self.txtUserID.set_can_focus(False)
        self.txtLastChanged.set_editable(False)
        self.txtLastChanged.set_can_focus(False)
        self.txtGroupID.set_editable(False)
        self.txtGroupID.set_can_focus(False)
        self.passwordChanged = False
        self.homeDirChanged = False
        self.tempFace = "/tmp/face.png"

        self.filterText(self.txtLoginName)
        self.filterText(self.txtGroupName)
        self.filterText(self.cmbPrimaryGroupEntry)

        # Treeviews
        self.tvHandlerUsersMain = TreeViewHandler(self.tvUsersMain)
        self.tvHandlerUserGroupsMain = TreeViewHandler(self.tvUserGroupsMain)
        self.tvHandlerUserGroups = TreeViewHandler(self.tvUserGroups)
        self.tvHandlerAccounts = TreeViewHandler(self.tvAccounts)
        self.tvHandlerSelectedAccounts = TreeViewHandler(self.tvSelectedAccounts)
        self.tvHandlerGroupsMain = TreeViewHandler(self.tvGroupsMain)
        self.tvHandlerGroupAccounts = TreeViewHandler(self.tvGroupAccounts)
        # Comboboxes
        self.cmbHandlerShells = ComboBoxHandler(self.cmbShells)
        self.cmbHandlerPrimaryGroup = ComboBoxHandler(self.cmbPrimaryGroup)
        self.cmbHandlerValidUntilMonth = ComboBoxHandler(self.cmbValidUntilMonth)

        # Get data
        self.refreshData()
        self.cmbHandlerShells.fillComboBox(self.shells)
        self.cmbHandlerValidUntilMonth.fillComboBox(functions.getMonthsList())
        year = datetime.now().year
        adj = Gtk.Adjustment(value=year, lower=year, upper=year + 10, step_incr=1, page_incr=0, page_size=0)
        self.spbValidUntilYear.set_adjustment(adj)

        # Connect the signals and show the window
        self.builder.connect_signals(self)
        self.window.show()


    # ===============================================
    # User functions
    # ===============================================

    def on_tvUsersMain_cursor_changed(self, widget, event=None):
        self.showUserData()

    def on_tvUsersMain_row_activated(self, widget, path, column):
        self.on_btnUserEdit_clicked(None)

    def on_btnUserAdd_clicked(self, widget):
        self.imgFace.set_from_pixbuf(self.usr.getUserFacePixbuf())
        self.tvHandlerUserGroups.fillTreeview(contentList=self.getUserGroupsComplete(), columnTypesList=['bool', 'str'])
        self.cmbHandlerShells.selectValue('/bin/bash')
        self.cmbHandlerPrimaryGroup.fillComboBox(self.groups)
        self.txtLoginName.set_editable(True)
        self.txtLoginName.set_can_focus(True)
        self.txtLoginName.set_text("new_user")
        self.txtUserID.set_text(str(self.usr.getNewUserID()))
        self.updateNewLogin()
        self.txtPassword.set_text("")
        self.radValidUntilAlways.set_active(True)
        self.windowUser.show()

    def on_btnUserEdit_clicked(self, widget):
        if self.selectedUser is not None:
            if not self.userFace is None:
                self.imgFace.set_from_pixbuf(self.userFace)
                self.imgFace.show()
                self.nbUser.get_nth_page(2).show()

            else:
                self.imgFace.hide()
                # Hide passwords tab
                self.nbUser.get_nth_page(2).hide()

            self.txtLoginName.set_editable(False)
            self.txtLoginName.set_can_focus(False)
            self.txtLoginName.set_text(self.user['user'].pw_name)
            if ",,," in self.user['user'].pw_gecos:
                self.txtRealName.set_text(self.user['user'].pw_name)
            else:
                self.txtRealName.set_text(self.user['user'].pw_gecos)
            self.txtUserID.set_text(str(self.user['user'].pw_uid))
            self.txtHomeDirectory.set_text(self.user['user'].pw_dir)
            self.tvHandlerUserGroups.fillTreeview(contentList=self.getUserGroupsComplete(self.user['groups']), columnTypesList=['bool', 'str'])
            self.cmbHandlerShells.selectValue(self.user['user'].pw_shell)
            self.cmbHandlerPrimaryGroup.fillComboBox(self.groups, self.user['prgrp'])
            self.txtPassword.set_text("")
            self.txtLastChanged.set_text(self.usr.intToDate(nr_days=self.user['pwd'].sp_lstchg, format_string='%d %B %Y', start_date=datetime(1970, 1, 1)))

            daysMin = self.user['pwd'].sp_min
            print((">>> daysMin = %d" % daysMin))
            if daysMin > 0:
                self.radValidUntilDate.set_active(True)
                dt = self.usr.intToDate(nr_days=daysMin)
                self.spbValidUntilDay.set_value(dt.day)
                self.cmbValidUntilMonth.set_active(dt.month - 1)
                self.spbValidUntilYear.set_value(dt.year)
            else:
                self.radValidUntilAlways.set_active(True)

            daysMax = self.user['pwd'].sp_max
            daysWarn = self.user['pwd'].sp_warn
            daysInact = self.user['pwd'].sp_inact
            print((">>> daysMax = %d" % daysMax))
            print((">>> daysWarn = %d" % daysWarn))
            print((">>> daysInact = %d" % daysInact))
            if daysMax < 1000 and daysWarn >= 0 and daysInact >= 0:
                self.chkRequirePasswordAfter.set_active(True)
                self.spbRequirePasswordAfter.set_value(daysMax)
                self.spbWarnBeforePasswordExpires.set_value(daysWarn)
                self.spbDisableAccountWhenPasswordExpires.set_value(daysInact)
            else:
                self.chkRequirePasswordAfter.set_active(False)

            daysExpire = self.user['pwd'].sp_expire
            print((">>> daysExpire = %d" % daysExpire))
            if daysExpire >= 0:
                self.chkEnforceMinimumPasswordAge.set_active(True)
                self.spbEnforceMinimumPasswordAge.set_value(daysExpire)
            else:
                self.chkEnforceMinimumPasswordAge.set_active(False)

            self.windowUser.show()

    def on_btnUserRemove_clicked(self, widget):
        # Remove user
        if self.selectedUser is not None:
            title = _("Remove user")
            if self.selectedUser != self.loggedinUser:
                qd = QuestionDialog(title, _("Are you sure you want to remove the following user:\n\n'%(user)s'") % { "user": self.selectedUser }, self.window)
                answer = qd.show()
                if answer:
                    # TODO
                    ret = self.usr.deleteUser(self.selectedUser)
                    if ret == "":
                        self.showInfo(title, _("User successfully removed: %(user)s") % {"user": self.selectedUser}, self.window)
                        self.refreshData()
                    else:
                        retMsg = "\n\n%s" % ret
                        self.showError(title, _("Could not remove user: %(user)s %(retmsg)s") % {"user": self.selectedUser, "retmsg": retMsg}, self.window)
            else:
                self.showError(title, _("You cannot remove the currently logged in user"), self.window)

    def on_chkShowSystemUsers_toggled(self, widget):
        self.refreshData()

    def on_btnBrowse_clicked(self, widget):
        directory = SelectDirectoryDialog(_('Select user directory'), self.txtHomeDirectory.get_text(), self.windowUser).show()
        if directory is not None:
            self.user['user'].pw_dir = directory
            self.txtHomeDirectory.set_text(self.user['user'].pw_dir)

    def on_radEnabled_toggled(self, widget):
        if widget.get_active():
            print(">>> Enable user")

    def on_radDisabled_toggled(self, widget):
        if widget.get_active():
            print(">>> Disable user")

    def on_radValidUntilAlways_toggled(self, widget):
        if widget.get_active():
            self.setValidUntil(False)

    def on_radValidUntilDate_toggled(self, widget):
        if widget.get_active():
            self.setValidUntil(True)

    def setValidUntil(self, boolean=True):
        self.spbValidUntilDay.set_sensitive(boolean)
        self.cmbValidUntilMonth.set_sensitive(boolean)
        self.spbValidUntilYear.set_sensitive(boolean)
        if not boolean:
            self.spbValidUntilDay.set_value(0)
            self.cmbValidUntilMonth.set_active(-1)
            self.spbValidUntilYear.set_value(0)

    def on_chkRequirePasswordAfter_toggled(self, widget):
        if widget.get_active():
            self.setRequirePasswordAfter(True)
        else:
            self.setRequirePasswordAfter(False)

    def setRequirePasswordAfter(self, boolean=True):
        self.spbRequirePasswordAfter.set_sensitive(boolean)
        self.spbWarnBeforePasswordExpires.set_sensitive(boolean)
        self.spbDisableAccountWhenPasswordExpires.set_sensitive(boolean)
        if not boolean:
            self.spbRequirePasswordAfter.set_value(0)
            self.spbWarnBeforePasswordExpires.set_value(0)
            self.spbDisableAccountWhenPasswordExpires.set_value(0)

    def on_chkEnforceMinimumPasswordAge_toggled(self, widget):
        if widget.get_active():
            self.setEnforceMinimumPasswordAge(True)
        else:
            self.setEnforceMinimumPasswordAge(False)

    def setEnforceMinimumPasswordAge(self, boolean=True):
        self.spbEnforceMinimumPasswordAge.set_sensitive(boolean)
        if not boolean:
            self.spbEnforceMinimumPasswordAge.set_value(0)

    def on_txtLoginName_changed(self, widget):
        self.updateNewLogin()

    def on_btnSaveUser_clicked(self, widget):
        errMsgs = []
        changed = False
        name = self.txtLoginName.get_text().strip()
        if name != "":
            userExists = self.usr.doesUserExist(name)

            realName = self.txtRealName.get_text().strip()
            if realName != "":
                if self.user['user'].pw_gecos == realName:
                    realName = ""
                else:
                    print(">>> realName changed")
                    changed = True

            prGroup = self.cmbHandlerPrimaryGroup.getValue()
            if prGroup != "":
                if self.user['prgrp'] == prGroup:
                    prGroup = ""
                else:
                    print(">>> prGroup changed")
                    changed = True
            elif not userExists:
                errMsgs.append(_("You need to provide a primary group for a new user"))

            home = self.txtHomeDirectory.get_text().strip()
            facePath = ""
            if home != "":
                if exists(self.tempFace):
                    facePath = join(home, ".face")
                if self.user['user'].pw_dir == home:
                    home = ""
                else:
                    print(">>> home changed")
                    changed = True

            groups = self.tvHandlerUserGroups.getToggledValues()
            if functions.areListsEqual(groups, self.user['groups']):
                groups = []
            else:
                print(">>> groups changed")
                changed = True

            password = self.txtPassword.get_text().strip()
            if password != "":
                encPwd = self.usr.encryptPassword(password)
                if self.user['pwd'].sp_pwd ==  encPwd:
                    password = ""
                else:
                    print(">>> password changed")
                    changed = True
            elif not userExists:
                errMsgs.append(_("You need to provide a password for a new user"))

        else:
            errMsgs.append(_("You need to provide a name for a new user"))

        shell = self.cmbHandlerShells.getValue()

        # TODO
        #if self.radValidUntilDate.get_active():
            #vuDay = self.spbValidUntilDay.get_value_as_int()
            #vuMonth = self.cmbValidUntilMonth.get_active() + 1
            #vuYear = self.spbValidUntilYear.get_value_as_int()
            #(datetime(vuYear, vuMonth, vuDay, 0, 0, 0) - datetime.now()).days

        #manageUser(self, user, primary_group="", group_list=[], shell="", home_dir="", full_name="", password="", expire_date="", inactive_days=""):
        title = _("Save user settings")
        if errMsgs:
            msg = "\n".join(errMsgs)
            self.showError(title, msg, self.windowUser)
        elif changed or facePath != "":
            err = 0
            if changed:
                err = self.usr.manageUser(user=name, full_name=realName, primary_group=prGroup, home_dir=home, group_list=groups, shell=shell, password=password)
            if err == 0:
                if exists(self.tempFace):
                    move(self.tempFace, facePath)
                self.showInfo(title, _("User saved: %(user)s") % {"user": name}, self.windowUser)
                self.refreshData()
            else:
                # TODO
                pass

            if exists(self.tempFace):
                os.remove(self.tempFace)
            self.windowUser.hide()
        else:
            self.showInfo(title, _("Nothing was changed on user: %(user)s") % {"user": name}, self.windowUser)
            self.windowUser.hide()

        if exists(self.tempFace):
            os.remove(self.tempFace)

    def on_cmbValidUntilMonth_changed(self, widget):
        monthDays = functions.getDaysInMonth(widget.get_active() + 1)
        adj = Gtk.Adjustment(value=1, lower=1, upper=monthDays, step_incr=1, page_incr=0, page_size=0)
        self.spbValidUntilDay.set_adjustment(adj)
        self.spbValidUntilDay.set_value(1)

    def updateNewLogin(self):
        txt = self.txtLoginName.get_text()
        self.txtRealName.set_text(txt)
        self.txtHomeDirectory.set_text("/home/%s" % txt)
        self.cmbHandlerPrimaryGroup.setValue(txt)

    def getUsers(self):
        self.users = []
        self.usersInfo = self.usr.getAllUsersInfoDict(self.chkShowSystemUsers.get_active())
        for ui in self.usersInfo:
            self.users.append([ui['face'], ui['user'].pw_name])

    def showUserData(self):
        # Show user groups in tvUserGroupsMain
        self.selectedUser = self.tvHandlerUsersMain.getSelectedValue(1)
        print((">>> selectedUser = %s" % self.selectedUser))
        for ui in self.usersInfo:
            if ui['user'].pw_name == self.selectedUser:
                self.user = ui
                break
        self.tvHandlerUserGroupsMain.fillTreeview(contentList=self.user['groups'], columnTypesList=['str'])
        self.userFace = self.usr.getUserFacePixbuf(self.user['user'].pw_name, None, 32)

    def getUserGroupsComplete(self, userGroups=None):
        ugc = []
        for group in self.groups:
            if group != self.user['prgrp']:
                isUg = False
                if userGroups is not None:
                    for ug in userGroups:
                        if ug == group:
                            isUg = True
                            break
                ugc.append([isUg, group])
        return ugc

    def on_btnCancelUser_clicked(self, widget):
        # Close add share window without saving
        if exists(self.tempFace):
            os.remove(self.tempFace)
        self.windowUser.hide()

    def on_ebFace_button_release_event(self, widget, data=None):
        imagePath = SelectImageDialog(_('Select user image'), self.user['user'].pw_dir, self.windowUser).show()
        if imagePath is not None:
            ih = ImageHandler(imagePath)
            ih.makeFaceImage(self.tempFace)
            if exists(self.tempFace):
                self.imgFace.set_from_pixbuf(ih.pixbuf)

    def on_usermanagerUserWindow_delete_event(self, widget, data=None):
        if exists(self.tempFace):
            os.remove(self.tempFace)
        self.windowUser.hide()
        return True

    def fillTreeViewUsers(self):
        self.tvHandlerUsersMain.fillTreeview(contentList=self.users, columnTypesList=['GdkPixbuf.Pixbuf', 'str'], fixedImgHeight=48)

    def on_ebFace_enter_notify_event(self, widget, data=None):
        self.windowUser.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def on_ebFace_leave_notify_event(self, widget, data=None):
        self.windowUser.get_window().set_cursor(None)


    # ===============================================
    # Group functions
    # ===============================================

    def on_tvGroupsMain_cursor_changed(self, widget, event=None):
        self.selectedGroup = self.tvHandlerGroupsMain.getSelectedValue()
        self.selectedGroupAccounts = self.usr.getGroupAccounts(self.selectedGroup)
        print((">>> selectedGroup 1 =  %s" % str(self.selectedGroup)))
        print((">>> selectedGroupAccounts 1 =  %s" % str(self.selectedGroupAccounts)))
        self.tvHandlerGroupAccounts.fillTreeview(self.selectedGroupAccounts, ['str'])

    def on_tvGroupsMain_row_activated(self, widget, path, column):
        self.on_btnGroupEdit_clicked(None)

    def on_btnGroupAdd_clicked(self, widget):
        self.selectedGroup = None
        self.selectedGroupAccounts = None
        print((">>> selectedGroup 2 =  %s" % str(self.selectedGroup)))
        print((">>> selectedGroupAccounts 2 =  %s" % str(self.selectedGroupAccounts)))
        self.txtGroupName.set_editable(True)
        self.txtGroupName.set_can_focus(True)
        self.txtGroupName.set_text("")
        self.txtGroupID.set_text(str(self.usr.getNewGroupID()))
        self.fillTreeViewAccounts(self.users)
        self.windowGroup.show()

    def on_btnGroupEdit_clicked(self, widget):
        if self.selectedGroup is not None:
            availableAccounts = []
            groupAccounts = []
            for acc in self.users:
                if acc[1] in self.selectedGroupAccounts:
                    groupAccounts.append(acc)
                else:
                    availableAccounts.append(acc)

            self.fillTreeViewAccounts(availableAccounts, groupAccounts)
            self.txtGroupName.set_text(self.selectedGroup)
            self.txtGroupName.set_editable(False)
            self.txtGroupName.set_can_focus(False)
            self.txtGroupID.set_text(str(self.usr.getGroupID(self.selectedGroup)))
            self.tvAccounts.grab_focus()
            self.windowGroup.show()

    def on_btnGroupRemove_clicked(self, widget):
        # Remove group
        if self.selectedGroup is not None:
            title = _("Remove group")
            if self.selectedGroup != self.loggedinUserPrimaryGroup:
                qd = QuestionDialog(title, _("Are you sure you want to remove the following group:\n\n'%(group)s'") % { "group": self.selectedGroup }, self.windowGroup)
                answer = qd.show()
                if answer:
                    ret = self.usr.deleteGroup(self.selectedGroup)
                    if ret == "":
                        self.showInfo(title, _("Group successfully removed: %(group)s") % {"group": self.selectedGroup}, self.windowGroup)
                        self.refreshData()
                    else:
                        retMsg = "\n\n%s" % ret
                        self.showError(title, _("Could not remove group: %(group)s %(retmsg)s") % {"group": self.selectedGroup, "retmsg": retMsg}, self.windowGroup)
            else:
                self.showError(title, _("You cannot remove the currently logged in user's primary group"), self.windowGroup)

    def on_btnAddAccount_clicked(self, widget):
        rows = self.tvHandlerAccounts.getSelectedRows()
        for row in rows:
            self.tvHandlerAccounts.delRow(row[0])
            self.tvHandlerSelectedAccounts.addRow(row[1])

    def on_btnRemoveAccount_clicked(self, widget):
        # TODO: check if you want to remove an account from its own primary group
        rows = self.tvHandlerSelectedAccounts.getSelectedRows()
        for row in rows:
            acc = row[1][1]
            pg = self.usr.getUserPrimaryGroupName(acc)
            if pg != self.selectedGroup:
                self.tvHandlerSelectedAccounts.delRow(row[0])
                self.tvHandlerAccounts.addRow(row[1])
            else:
                self.showError(_("Remove account"), _("You cannot remove an account from its own primary group"), self.windowGroup)

    def on_btnOkGroup_clicked(self, widget):
        group = self.txtGroupName.get_text()
        if group != "":
            newSelAccs = self.tvHandlerSelectedAccounts.getColumnValues(1)

            if self.selectedGroupAccounts is not None:
                # New accounts in group
                for a in newSelAccs:
                    if a not in self.selectedGroupAccounts:
                        # Add group to account
                        self.usr.addGroupToAccount(a, group)

                # Removed accounts in group
                for a in self.selectedGroupAccounts:
                    if a not in newSelAccs:
                        # Remove group from account
                        self.usr.removeGroupFromAccount(a, group)
            else:
                # Create new group
                self.usr.createGroup(group)
                # Add group to each selected account
                for a in newSelAccs:
                    self.usr.addGroupToAccount(a, group)

            # Close the user window
            self.windowGroup.hide()
            self.refreshData()

    def on_btnCancelGroup_clicked(self, widget):
        self.windowGroup.hide()

    def on_usermanagerGroupWindow_delete_event(self, widget, data=None):
        self.windowGroup.hide()
        return True

    def on_tvAccounts_row_activated(self, widget, path, column):
        self.on_btnAddAccount_clicked(None)

    def on_tvSelectedAccounts_row_activated(self, widget, path, column):
        self.on_btnRemoveAccount_clicked(None)

    def fillTreeViewAccounts(self, availableAccounts, selectedAccounts=None):
        if (availableAccounts is None or not availableAccounts) and selectedAccounts:
            # Dirty hack to prepare the available accounts treeview
            self.tvHandlerAccounts.fillTreeview(contentList=selectedAccounts, columnTypesList=['GdkPixbuf.Pixbuf', 'str'], fixedImgHeight=24)
            self.tvHandlerAccounts.clearTreeView()
        else:
            self.tvHandlerAccounts.fillTreeview(contentList=availableAccounts, columnTypesList=['GdkPixbuf.Pixbuf', 'str'], fixedImgHeight=24)

        if (selectedAccounts is None or not selectedAccounts) and availableAccounts:
            # Dirty hack to prepare the selected accounts treeview
            self.tvHandlerSelectedAccounts.fillTreeview(contentList=availableAccounts, columnTypesList=['GdkPixbuf.Pixbuf', 'str'], fixedImgHeight=24)
            self.tvHandlerSelectedAccounts.clearTreeView()
        else:
            self.tvHandlerSelectedAccounts.fillTreeview(contentList=selectedAccounts, columnTypesList=['GdkPixbuf.Pixbuf', 'str'], fixedImgHeight=24)

    def fillTreeViewGroups(self):
        self.tvHandlerGroupsMain.fillTreeview(contentList=self.groups, columnTypesList=['str'])
        self.on_tvGroupsMain_cursor_changed(None)

    # ===============================================
    # General functions
    # ===============================================

    def refreshData(self):
        self.getUsers()
        self.groups = self.usr.getGroups()
        self.fillTreeViewUsers()
        self.fillTreeViewGroups()
        self.showUserData()

    def showInfo(self, title, message, parent):
        MessageDialogSave(title, message, Gtk.MessageType.INFO, parent).show()

    def showError(self, title, message, parent):
        MessageDialogSave(title, message, Gtk.MessageType.ERROR, parent).show()

    def filterText(self, widget):
        def filter(entry, *args):
            text = entry.get_text().strip().lower()
            entry.set_text(''.join([i for i in text if i in '0123456789abcdefghijklmnopqrstuvwxyz-._']))
        widget.connect('changed', filter)

    # Close the gui
    def on_usermanagerWindow_destroy(self, widget):
        # Close the app
        Gtk.main_quit()

if __name__ == '__main__':
    # Create an instance of our GTK application
    try:
        gui = UserManager()
        Gtk.main()
    except KeyboardInterrupt:
        pass
