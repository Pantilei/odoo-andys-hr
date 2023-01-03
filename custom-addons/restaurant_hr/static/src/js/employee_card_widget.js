/** @odoo-module **/

import AbstractFieldOwl from "web.AbstractFieldOwl";
import fieldRegistryOwl from "web.field_registry_owl";

const { useState, onWillUpdateProps, onMounted, useRef } = owl.hooks;

export default class EmployeeCard extends AbstractFieldOwl {
  constructor(...args) {
    super(...args);
  }

  setup() {
    super.setup();

    this.state = useState({
      employeeCardData: JSON.parse(this.value),
    });
    onWillUpdateProps(async (nextProps) => {
      this.state.employeeCardData = JSON.parse(this.value);
    });

    onMounted(() => {});
  }
}

EmployeeCard.template = "EmployeeCard";
EmployeeCard.components = {};

fieldRegistryOwl.add("employee_card_widget", EmployeeCard);
