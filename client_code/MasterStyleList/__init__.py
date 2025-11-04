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
