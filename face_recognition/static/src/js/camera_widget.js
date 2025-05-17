/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";

export class CameraWidget extends Component {
    setup() {
        onMounted(this.startCamera);
    }

    startCamera() {
        const video = this.el.querySelector('video');
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    video.srcObject = stream;
                })
                .catch((err) => {
                    console.error("Tidak bisa mengakses kamera:", err);
                });
        }
    }
}

CameraWidget.template = "face_recognition.CameraWidget";
