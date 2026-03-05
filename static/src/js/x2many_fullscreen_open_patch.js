/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";

patch(X2ManyField.prototype, {
    async openRecord(record) {
        const isMedidasList =
            this.props.record.resModel === "levantamiento.medida" && this.props.name === "linea_ids";
        const isSharedEventosList =
            this.props.record.resModel === "levantamiento.medida" && this.props.name === "evento_ids";
        const isEventosList =
            this.props.record.resModel === "levantamiento.linea" &&
            ["log_ids", "log_event_ids"].includes(this.props.name);

        if (isMedidasList || isSharedEventosList || isEventosList) {
            return this.switchToForm(record);
        }
        return super.openRecord(...arguments);
    },
});
