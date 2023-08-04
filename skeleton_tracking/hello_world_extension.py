import os
from omni.isaac.examples.base_sample import BaseSampleExtension
from omni.isaac.examples.user_examples import HelloWorld
from omni.isaac.ui.ui_utils import btn_builder
import omni.ui as ui
import asyncio

class HelloWorldExtension(BaseSampleExtension):
    def on_startup(self, ext_id: str):
        super().on_startup(ext_id)
        super().start_extension(
            menu_name="",
            submenu_name="",
            name="Meta-Sejong",
            title="Meta-Sejong",
            doc_link="https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/tutorial_core_hello_world.html",
            overview="This Example introduces the user on how to do cool stuff with Isaac Sim through scripting in asynchronous mode.",
            file_path=os.path.abspath(__file__),
            sample=HelloWorld(),
            number_of_extra_frames=1,
            
        )
        
        self.task_ui_elements = {}
        frame = self.get_frame(index=0)
        self.build_task_controls_ui(frame)

        return
    
    
    def _on_start_party_button_event(self):
        asyncio.ensure_future(self.sample._on_start_party_event_async())
        self.task_ui_elements["Human"].enabled = False
        return
    
    def post_reset_button_event(self):
        self.task_ui_elements["Human"].enabled = True
        # self.sample._on_reset_party_event_async()
        return

    def post_load_button_event(self):
        self.task_ui_elements["Human"].enabled = True
        return

    def post_clear_button_event(self):
        self.task_ui_elements["Human"].enabled = False
        return
    
    def build_task_controls_ui(self, frame):
        with frame:
            with ui.VStack(spacing=5):
                # Update the Frame Title
                frame.title = "Task Controls"
                frame.visible = True
                dict = {
                    "label": "Human",
                    "type": "button",
                    "text": "Human",
                    "tooltip": "Human",
                    "on_clicked_fn": self._on_start_party_button_event,
                }

                self.task_ui_elements["Human"] = btn_builder(**dict)
                self.task_ui_elements["Human"].enabled = False