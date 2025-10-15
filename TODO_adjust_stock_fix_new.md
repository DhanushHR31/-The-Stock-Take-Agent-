# TODO: Fix Adjust Stock Functionality and Improve UI Graphics

- [ ] Add GET /adjust-stock route in ganana/app/web.py to render adjust_stock.html with queried data (all_inventory, all_stock_takes, all_stock_counts, adjustment_logs).
- [ ] Fix ganana/app/templates/adjust_stock.html inventory tab to display inventory levels instead of stock counts.
- [ ] Update ganana/app/api/adjustment.py: change setattr to direct assignment for quantity_on_hand, add try-except for db.commit().
- [ ] Enhance ganana/app/static/theme.css with modern graphics: gradients, animations, shadows, better icons for improved UI.
- [ ] Test the adjust stock functionality: run app, adjust stock, verify inventory updates and logs are saved/displayed.
- [ ] Verify UI improvements across the project for consistency.
