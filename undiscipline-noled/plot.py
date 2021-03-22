import pcbnew

plots = {
    "front": {
        "negative": True,
        "layers": [pcbnew.Edge_Cuts, pcbnew.F_Cu]
    },
    "back": {
        "negative": True,
        "layers": [pcbnew.Edge_Cuts, pcbnew.B_Cu]
    }
}

pcb = pcbnew.LoadBoard("undiscipline-noled.kicad_pcb")

for plot, conf in plots.items():
    plotctrl = pcbnew.PLOT_CONTROLLER(pcb)
    plotopt = plotctrl.GetPlotOptions()
    plotopt.SetOutputDirectory("plots/")
    plotopt.SetNegative(conf.get("negative", False))
    plotopt.SetMirror(conf.get("mirror", False))
    plotctrl.OpenPlotfile(plot, pcbnew.PLOT_FORMAT_SVG, plot)
    for layer in conf['layers']:
        plotctrl.SetLayer(layer)
        plotctrl.PlotLayer()
    plotctrl.ClosePlot()
