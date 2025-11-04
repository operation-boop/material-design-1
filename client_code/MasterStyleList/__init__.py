from ._anvil_designer import MasterStyleListTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime

class MasterStyleList(MasterStyleListTemplate):
  """Main list view for Master Styles"""

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Initialize filters
    self.current_filters = {}
    self.load_filter_options()
    self.refresh_list()

  def load_filter_options(self):
    """Populate filter dropdowns"""
    # Client filter
    clients = app_tables.clients.search()
    self.client_filter_dropdown.items = [("All Clients", None)] + [
      (f"{c['name']} ({c['country']})", c.get_id()) for c in clients
    ]

    # Price category filter
    self.price_category_dropdown.items = [
      ("All Categories", None),
      ("Low", "Low"),
      ("Medium", "Medium"),
      ("High", "High")
    ]

    # Country filter
    self.country_filter_dropdown.items = [
      ("All Countries", None),
      ("🇬🇧 UK", "UK"),
      ("🇺🇸 US", "US"),
      ("🇦🇺 Australia", "Australia")
    ]

  def refresh_list(self):
    """Load and display master styles based on filters"""
    # Build query
    query_params = {}

    if self.current_filters.get('client_id'):
      query_params['client'] = app_tables.clients.get_by_id(self.current_filters['client_id'])

    if self.current_filters.get('search_term'):
      # Anvil doesn't support OR queries easily, so we'll filter in Python
      pass

    # Get all master styles
    styles = app_tables.master_styles.search(**query_params)

    # Apply additional filters in Python if needed
    if self.current_filters.get('price_category'):
      styles = [s for s in styles if s['client']['price_category'] == self.current_filters['price_category']]

    if self.current_filters.get('country'):
      styles = [s for s in styles if s['client']['country'] == self.current_filters['country']]

    if self.current_filters.get('search_term'):
      term = self.current_filters['search_term'].lower()
      styles = [s for s in styles 
                if term in s['ref_id'].lower() 
                or term in s['description'].lower()
                or term in s['client']['name'].lower()]

    # Sort by created date (newest first)
    styles = sorted(styles, key=lambda x: x['created_at'], reverse=True)

    # Clear existing items
    self.style_list_panel.clear()

    # Add style cards
    for style in styles:
      card = MasterStyleCard(style=style, parent_form=self)
      self.style_list_panel.add_component(card)

    # Update count
    self.results_count_label.text = f"Showing {len(styles)} styles"

  def client_filter_dropdown_change(self, **event_args):
    """Filter by client"""
    self.current_filters['client_id'] = self.client_filter_dropdown.selected_value
    self.refresh_list()

  def price_category_dropdown_change(self, **event_args):
    """Filter by price category"""
    self.current_filters['price_category'] = self.price_category_dropdown.selected_value
    self.refresh_list()

  def country_filter_dropdown_change(self, **event_args):
    """Filter by country"""
    self.current_filters['country'] = self.country_filter_dropdown.selected_value
    self.refresh_list()

  def search_box_pressed_enter(self, **event_args):
    """Search when user presses enter"""
    self.current_filters['search_term'] = self.search_box.text
    self.refresh_list()

  def search_button_click(self, **event_args):
    """Search button clicked"""
    self.current_filters['search_term'] = self.search_box.text
    self.refresh_list()

  def clear_filters_button_click(self, **event_args):
    """Clear all filters"""
    self.current_filters = {}
    self.client_filter_dropdown.selected_value = None
    self.price_category_dropdown.selected_value = None
    self.country_filter_dropdown.selected_value = None
    self.search_box.text = ""
    self.refresh_list()

  def new_style_button_click(self, **event_args):
    """Open form to create new master style"""
    from .MasterStyleForm import MasterStyleForm
    result = alert(
      content=MasterStyleForm(style=None),
      large=True,
      buttons=[("Save", True), ("Cancel", False)]
    )
    if result:
      self.refresh_list()


class MasterStyleCard(MasterStyleCardTemplate):
  """Individual style card in the list"""

  def __init__(self, style=None, parent_form=None, **properties):
    self.init_components(**properties)
    self.style = style
    self.parent_form = parent_form
    self.populate_card()

  def populate_card(self):
    """Fill card with style data"""
    if not self.style:
      return

    # Image
    if self.style['picture']:
      self.style_image.source = self.style['picture']
    else:
      self.style_image.source = "_/theme/placeholder-image.png"

    # Style info
    client = self.style['client']
    self.style_id_label.text = f"Style: {self.style.get_id()}"
    self.client_ref_label.text = f"Client Ref: {self.style['ref_id']}"

    # Client with flag emoji
    country_flags = {"UK": "🇬🇧", "US": "🇺🇸", "Australia": "🇦🇺"}
    flag = country_flags.get(client['country'], "")
    self.client_label.text = f"Client: {client['name']} ({client['price_category']}) {flag}"

    # Description (truncate if too long)
    desc = self.style['description']
    if len(desc) > 100:
      desc = desc[:97] + "..."
    self.description_label.text = f"Description: {desc}"

    # SKU count
    sku_count = len(app_tables.style_skus.search(master_style=self.style))
    rfq_count = self.get_active_rfq_count()
    self.stats_label.text = f"SKUs: {sku_count} variants | Active RFQs: {rfq_count}"

    # Created info
    created_date = self.style['created_at'].strftime("%b %d, %Y")
    created_by = self.style['created_by']['name']
    self.created_label.text = f"Created: {created_date} by {created_by}"

  def get_active_rfq_count(self):
    """Count active RFQs for this style"""
    # This would query RFQ line items
    # For now, return placeholder
    return 0

  def view_details_button_click(self, **event_args):
    """Open detail view"""
    from .MasterStyleDetail import MasterStyleDetail
    open_form('MasterStyleDetail', style=self.style)

  def quick_copy_button_click(self, **event_args):
    """Quick copy this style"""
    result = confirm(f"Create a copy of {self.style['ref_id']}?")
    if result:
      # Create copy logic here
      new_style = app_tables.master_styles.add_row(
        ref_id=f"{self.style['ref_id']}-COPY",
        client=self.style['client'],
        picture=self.style['picture'],
        description=f"Copy of: {self.style['description']}",
        created_at=datetime.now(),
        created_by=anvil.users.get_user()
      )
      Notification("Style copied successfully!").show()
      self.parent_form.refresh_list()

  def qr_code_button_click(self, **event_args):
    """Generate and show QR code"""
    from .QRCodeViewer import QRCodeViewer
    # Generate QR code for this style
    alert(
      content=QRCodeViewer(data=self.style.get_id()),
      title=f"QR Code: {self.style['ref_id']}",
      buttons=[("Close", True)]
    )