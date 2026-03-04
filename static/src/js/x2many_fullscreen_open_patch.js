/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";

patch(X2ManyField.prototype, {
    async openRecord(record) {
        const isMedidasList =
            this.props.record.resModel === "levantamiento.medida" && this.props.name === "linea_ids";
        const isEventosList =
            this.props.record.resModel === "levantamiento.linea" && this.props.name === "log_ids";

        if (isMedidasList || isEventosList) {
            return this.switchToForm(record);
        }
        return super.openRecord(...arguments);
    },
});
