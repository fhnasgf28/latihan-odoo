/** @odoo-module **/

import { mount } from "@odoo/owl";
import { CameraWidget } from "./components/camera_widget/camera_widget";

document.addEventListener("DOMContentLoaded", () => {
    const container = document.querySelector("#camera_widget");
    if (container) {
        mount(CameraWidget, { target: container });
    }
});
