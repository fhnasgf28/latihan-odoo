/** @odoo-module **/

import { mount, Component } from "@odoo/owl";

class OwlApp extends Component {
    static template = "odoo_owl_framework.MainComponent";
    state = {
        names: ["Alice", "Bob", "Charlie"],
        newName: "",
    };

    addName() {
        if (this.state.newName.trim()) {
            this.state.names.push(this.state.newName.trim());
            this.state.newName = "";
        }
    }

    onInput(ev) {
        this.state.newName = ev.target.value;
    }
}

mount(owlApp, document.getElementById("owl-app-root"));