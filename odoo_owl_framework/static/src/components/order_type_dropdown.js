// static/src/js/order_type_dropdown.js
/** @odoo-module **/
import { Component, useState } from '@odoo/owl';
import { registry } from '@web/core/registry';

export class OrderTypeDropdown extends Component {
    setup() {
        this.state = useState({ value: this.props.value || '' });
    }

    onChange(ev) {
        this.state.value = ev.target.value;
        this.props.update(this.state.value); // Wajib agar Odoo tahu ada perubahan!
    }
}
OrderTypeDropdown.template = 'odoo_owl_framework.OrderTypeDropdown';

registry.category('fields').add('owl_order_type_dropdown', OrderTypeDropdown);
