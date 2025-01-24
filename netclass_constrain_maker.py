import wx
import pcbnew

class NetclassInfoPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Netclass Information"
        self.category = "PCB Analysis"
        self.description = "Lists netclasses and their unique associated nets, and generates custom DRC rules"
        self.icon_file_name = ""

    def Run(self):
        board = pcbnew.GetBoard()
        netclass_data = {}
        net_lengths = {}

        # Go through all tracks to build netclass information and total lengths
        for track in board.GetTracks():
            netclass_name = track.GetNetClassName()
            net_name = track.GetNetname()
            net_length = track.GetLength() / 1e6  # Convert from nanometers to millimeters

            if netclass_name not in netclass_data:
                netclass_data[netclass_name] = set()
            netclass_data[netclass_name].add(net_name)

            if net_name in net_lengths:
                net_lengths[net_name] += net_length
            else:
                net_lengths[net_name] = net_length

        # Include pads as well (they won't add length, but might belong to a net)
        for pad in board.GetPads():
            netclass_name = pad.GetNetClassName()
            net_name = pad.GetNetname()
            if netclass_name not in netclass_data:
                netclass_data[netclass_name] = set()
            netclass_data[netclass_name].add(net_name)

        # Calculate the maximum length for each netclass
        netclass_max_length = {}
        for nc_name, nets in netclass_data.items():
            max_len = 0.0
            for net_name in nets:
                length_val = net_lengths.get(net_name, 0.0)
                if length_val > max_len:
                    max_len = length_val
            netclass_max_length[nc_name] = max_len

        def get_net_length(net_name):
            """Returns the length in millimeters of the specified net, or 'Unknown' if not found."""
            return net_lengths.get(net_name, 'Unknown')

        # This list will store the netclasses that are currently displayed
        currently_shown_netclasses = []

        # Create the dialog
        dialog = wx.Dialog(None, title="Netclass Information")
        dialog.SetSize((1200, 900))
        panel = wx.Panel(dialog)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create GUI controls
        input_label = wx.StaticText(panel, label="Enter Netclass Names (comma-separated):")
        netclass_input = wx.TextCtrl(panel, size=(1100, -1))
        text_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(1100, 500))

        filter_button = wx.Button(panel, label="Filter")
        all_button = wx.Button(panel, label="ALL")
        drc_button = wx.Button(panel, label="Show DRC Rules")
        close_button = wx.Button(panel, label="Close")

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(filter_button, 0, wx.ALL, 5)
        button_sizer.Add(all_button, 0, wx.ALL, 5)
        button_sizer.Add(drc_button, 0, wx.ALL, 5)
        button_sizer.Add(close_button, 0, wx.ALL, 5)

        # Helper function to display info about a set of netclasses
        def display_netclasses_info(netclasses):
            text_box.Clear()
            for netclass_name in netclasses:
                if netclass_name in netclass_data:
                    text_box.AppendText(f"Netclass: {netclass_name}\n")
                    text_box.AppendText("Nets:\n")
                    for net_name in netclass_data[netclass_name]:
                        net_len = get_net_length(net_name)
                        text_box.AppendText(f"  - {net_name} (Length: {net_len} mm)\n")
                    text_box.AppendText(f"Maximum length: {netclass_max_length[netclass_name]:.3f} mm\n\n")
                else:
                    text_box.AppendText(f"Netclass '{netclass_name}' not found.\n\n")

        # FILTER button callback
        def on_filter(event):
            # Parse user input (comma-separated netclass names)
            input_netclasses = [nc.strip() for nc in netclass_input.GetValue().split(',') if nc.strip()]

            # Filter only the netclasses that exist in netclass_data
            filtered = []
            for nc in input_netclasses:
                if nc in netclass_data:
                    filtered.append(nc)

            nonlocal currently_shown_netclasses
            currently_shown_netclasses = filtered

            # Display the information for these filtered netclasses
            display_netclasses_info(currently_shown_netclasses)

        # ALL button callback
        def on_all(event):
            nonlocal currently_shown_netclasses
            all_nc = list(netclass_data.keys())
            currently_shown_netclasses = sorted(all_nc)  # sort if desired
            display_netclasses_info(currently_shown_netclasses)

        # Show DRC Rules button callback
        def on_show_drc(event):
            text_box.Clear()
            text_box.AppendText("(version 1)\n\n")

            # Generate rules only for the currently displayed netclasses
            for nc_name in currently_shown_netclasses:
                max_len = netclass_max_length.get(nc_name, 0.0)
                text_box.AppendText(
                    f"(rule {nc_name}_LENGTH\n"
                    f"\t(condition \"A.NetClass=='{nc_name}'\")\n"
                    f"\t(constraint length (opt {max_len:.3f}mm))\n"
                    f")\n\n"
                )
            text_box.AppendText("; -- End of generated DRC rules --\n")

        # Close button callback
        def on_close(event):
            dialog.EndModal(wx.ID_CLOSE)

        # Bind events
        filter_button.Bind(wx.EVT_BUTTON, on_filter)
        all_button.Bind(wx.EVT_BUTTON, on_all)
        drc_button.Bind(wx.EVT_BUTTON, on_show_drc)
        close_button.Bind(wx.EVT_BUTTON, on_close)

        # Layout
        main_sizer.Add(input_label, 0, wx.ALL, 10)
        main_sizer.Add(netclass_input, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(text_box, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        panel.SetSizer(main_sizer)
        main_sizer.Fit(dialog)

        dialog.ShowModal()
        dialog.Destroy()

# Register the plugin
NetclassInfoPlugin().register()
