# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleSourcedByLine(TransactionCase):
    def setUp(self):
        super(TestSaleSourcedByLine, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]
        self.stock_move_model = self.env["stock.move"]

        # Refs
        self.customer = self.env.ref("base.res_partner_2")
        self.product_1 = self.env.ref("product.product_product_27")
        self.product_2 = self.env.ref("product.product_product_24")
        self.warehouse_shop0 = self.env.ref("stock.stock_warehouse_shop0")
        self.warehouse0 = self.env.ref("stock.warehouse0")

    def test_sales_order_multi_source(self):
        so = self.sale_order_model.create({"partner_id": self.customer.id})
        self.sale_order_line_model.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse_shop0.id,
                "order_id": so.id,
            }
        )
        self.sale_order_line_model.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse0.id,
                "order_id": so.id,
            }
        )
        # confirm quotation
        so.action_confirm()
        self.assertEquals(
            len(so.picking_ids),
            2,
            "2 delivery orders expected. Got %s instead" % len(so.picking_ids),
        )
        for line in so.order_line:
            self.assertEquals(
                line.procurement_group_id.name,
                line.order_id.name + "/" + line.warehouse_id.name,
                "The name of the procurement group is not " "correct.",
            )
            for move in line.move_ids:
                self.assertEquals(
                    move.group_id,
                    line.procurement_group_id,
                    "The group in the stock move does not "
                    "match with the procurement group in "
                    "the sales order line.",
                )
                self.assertEquals(
                    move.picking_id.group_id,
                    line.procurement_group_id,
                    "The group in the stock picking does "
                    "not match with the procurement group "
                    "in the sales order line.",
                )

    def test_sales_order_no_source(self):
        so = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "warehouse_id": self.warehouse_shop0.id,
                "company_id": self.warehouse_shop0.company_id.id,
            }
        )
        self.sale_order_line_model.create(
            {"product_id": self.product_1.id, "product_uom_qty": 8, "order_id": so.id}
        )
        self.sale_order_line_model.create(
            {"product_id": self.product_2.id, "product_uom_qty": 8, "order_id": so.id}
        )
        # confirm quotation
        so.action_confirm()
        self.assertEquals(
            len(so.picking_ids),
            1,
            "1 delivery order expected. Got %s instead" % len(so.picking_ids),
        )

    def test_sale_order_source(self):
        so = self.sale_order_model.create({"partner_id": self.customer.id})
        self.sale_order_line_model.create(
            {
                "product_id": self.product_1.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse_shop0.id,
                "order_id": so.id,
            }
        )
        self.sale_order_line_model.create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 8,
                "warehouse_id": self.warehouse0.id,
                "order_id": so.id,
            }
        )
        # confirm quotation
        so.action_confirm()
        for line in so.order_line:
            for stock_move in line.move_ids:
                self.assertEquals(
                    stock_move.warehouse_id,
                    line.warehouse_id,
                    "The warehouse in the stock.move does not "
                    "match with the Sales order line.",
                )
