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
