/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import ActionMenus from "web.ActionMenus";

/**
 * This is a patch of the new Dialog class.
 * Its purpose is to inform the old "active/inactive" mechanism.
 */
patch(ActionMenus.prototype, "remove tooltips", {
  setup() {
    this.actionButtonStrings = {
      title: this.env._t("Action"),
    };
    this.printButtonStrings = {
      title: this.env._t("Print"),
    };
  },
});
