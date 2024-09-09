import sys
import clr          # clr is  in pythonnet library 2.5.2
#AP_API_Dll_path = r"C:\Program Files\Audio Precision\APx500 6.1\API"    #   Register the Audio Precision API DLL to use
AP_API_Dll_path = r"C:\Program Files\Audio Precision\APx500 4.5\API"
# AP_API_Dll_path = r"C:\Program Files\Audio Precision\APx500 5.0\API"

sys.path.append(AP_API_Dll_path)   
                                
clr.AddReference("AudioPrecision.API2")                                 # Adding Reference 
clr.AddReference("AudioPrecision.API") 	                                # Adding Reference 

from AudioPrecision.API import *
from .AudioPrecision import *

#Serial digital

Format = ['I2S', 'DSP', 'Custom']

#   Filter settings
HP = ['DC', 'AC', 'Butterworth', 'Elliptic']
LP = ['ADC passband', 'AES17 (20kHz)', 'AES17 (40kHz)', 'Butterworth', 'Elliptic']
BW = ['22.4k' , '45k', '90k', '250k', '500k', '1M']
Weight = ['None', 'A-wt.', 'B-wt.', 'C-wt.', 'CCIR-1k', 'CCIR-2k', 'CCITT', 'C-Message', '50 us de-emph.', '75 us de-emph.', '50 us de-emph. + A-wt.', '75 us de-emph. + A-wt.']

#   Sweep
SourceSweep = {'Gen Freq' : 1,
'Gen. Level' : 9 }

#   FFT
FFT_Length = ['256', '512', '1k', '2k', '4k', '8k', '12k', '16k', '24k', '32k', '48k', '64k', '96k', '128k', '192k', '256k', '300k', '512k', '600k', '1M', '1.2M']
Bandwidth = ['2.75k', '3.5k', '5.5k', '7k', '11k', '20k', '22.4k', '40k', '45k', '80k', '90k', '250k', '500k', '1M', 'Use Signal Path']

# Recorder

Bit_Depth = ['16', '24', 'Auto']
Format_Wav = ['Multiple Mono PCM', 'Multi-channel PCM', 'Extensible Multi-channel PCM']
Read_rate = ['1', '2', '4', '8', '16', '32', '64', '125', '250']

class AP555:

    def __init__(self, mode = 'BenchMode', fullpath =''):
        self.APx = APx500_Application()
        if fullpath != '':
            self.APx.OpenProject(fullpath) 
        if mode == 'BenchMode':
            self.APx.OperatingMode = False                              #Bench mode   
        else:                                                                    
            self.APx.OperatingMode = True                               #Sequence mode
        self.APx.Visible = 1

################### Input / Output Settings ##########################


    def Output_Input_Configuration(self, Port = 'Output', Connector = 'Digital Serial' , Channels = 2):
        if Port == 'Output':
            if Connector == 'Analog Unbalanced':
                self.APx.BenchMode.Setup.OutputConnector.Type = OutputConnectorType.AnalogUnbalanced
                self.APx.BenchMode.Setup.AnalogOutput.ChannelCount = Channels
            elif Connector == 'Analog Balanced':
                self.APx.BenchMode.Setup.OutputConnector.Type = OutputConnectorType.AnalogBalanced
                self.APx.BenchMode.Setup.AnalogOutput.ChannelCount = Channels
            elif Connector == 'Digital Serial':
                self.APx.BenchMode.Setup.OutputConnector.Type = OutputConnectorType.DigitalSerial
            elif Connector == 'PDM':
                self.APx.BenchMode.Setup.OutputConnector.Type = OutputConnectorType.PDM
            else:
                return(False)  
        else:      #Input
            if Connector == 'Analog Unbalanced':
                self.APx.BenchMode.Setup.InputConnector.Type = InputConnectorType.AnalogUnbalanced
                self.APx.BenchMode.Setup.AnalogInput.ChannelCount = Channels
            elif Connector == 'Analog Balanced':
                self.APx.BenchMode.Setup.InputConnector.Type = InputConnectorType.AnalogBalanced
                self.APx.BenchMode.Setup.AnalogInput.ChannelCount = Channels
            elif Connector == 'Digital Serial':
                self.APx.BenchMode.Setup.InputConnector.Type = InputConnectorType.DigitalSerial
            elif Connector == 'PDM':
                self.APx.BenchMode.Setup.InputConnector.Type = InputConnectorType.PDM
            else:
                return(False)  

        return(True)
        
        
           
    def Configure_DigitalSerial(self, Port = 'Transmitter', path = r"", Channels = 2, SerialFormat = 'I2S', BitShift = True, WordWidth = 32, Dept = 24, FSYN = 48000, Level = '1.8 V'):
        if Port == 'Transmitter':
            if path != r"":     #.stx file
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.Open(path)
                self.APx.BenchMode.Setup.OutputConnector.Type = OutputConnectorType.DigitalSerial
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.Channels = Channels
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.MsbFirst = True
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.Format = Format.index(SerialFormat)
                if SerialFormat == 'Custom': 
                    self.APx.BenchMode.Setup.SerialDigitalTransmitter.DataJustification = SerialCustomDataJustification.LeftJustified
                    self.APx.BenchMode.Setup.SerialDigitalTransmitter.FrameClockPulseWidth = FrameClockPulseWidth.OneSubframe
            
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.FrameClockLeftOneBit = BitShift  
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.WordWidth = WordWidth
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.BitDepth = Dept
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.MasterClockSource = MasterClockSource.Internal
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.BitFrameClockDirection = ClockDirection.Out
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.BitClkSendEdgeSync = EdgeSync.FallingEdge
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.ScaleFreqByFixedRate = FSYN
                if Level == '1.8 V':
                    self.APx.BenchMode.Setup.SerialDigitalTransmitter.LogicLevel = 0
                elif Level == '2.5 V':
                    self.APx.BenchMode.Setup.SerialDigitalTransmitter.LogicLevel = 1
                else :  #3.3 V
                    self.APx.BenchMode.Setup.SerialDigitalTransmitter.LogicLevel = 2
            else:
                self.APx.BenchMode.Setup.SerialDigitalTransmitter.Open(path)       
        else:       #Receiver
            if path != r"": #.srx file
                self.APx.BenchMode.Setup.InputConnector.Type = InputConnectorType.DigitalSerial
                self.APx.BenchMode.Setup.SerialDigitalReceiver.Channels = Channels
                self.APx.BenchMode.Setup.SerialDigitalReceiver.MsbFirst = True
                if SerialFormat == 'Custom': 
                    self.APx.BenchMode.Setup.SerialDigitalReceiver.DataJustification = SerialCustomDataJustification.LeftJustified
                    self.APx.BenchMode.Setup.SerialDigitalReceiver.FrameClockPulseWidth = FrameClockPulseWidth.OneSubframe

                self.APx.BenchMode.Setup.SerialDigitalReceiver.FrameClockLeftOneBit = BitShift
                self.APx.BenchMode.Setup.SerialDigitalReceiver.WordWidth = WordWidth
                self.APx.BenchMode.Setup.SerialDigitalReceiver.BitDepth = Dept
                self.APx.BenchMode.Setup.SerialDigitalReceiver.MasterClockSource = MasterClockSource.Internal
                self.APx.BenchMode.Setup.SerialDigitalReceiver.BitFrameClockDirection = ClockDirection.Out
                self.APx.BenchMode.Setup.SerialDigitalReceiver.BitClkSendEdgeSync = EdgeSync.FallingEdge
                self.APx.BenchMode.Setup.SerialDigitalReceiver.ScaleFreqByFixedRate = FSYN
                if Level == '1.8 V':
                    self.APx.BenchMode.Setup.SerialDigitalReceiver.LogicLevel = 0
                elif Level == '2.5 V':
                    self.APx.BenchMode.Setup.SerialDigitalReceiver.LogicLevel = 1
                else :  #3.3 V
                    self.APx.BenchMode.Setup.SerialDigitalReceiver.LogicLevel = 2
            else:
                self.APx.BenchMode.Setup.SerialDigitalReceiver.Open(path)        

    def Enable_Digital_Serial(self, Port = "Transmitter", state = True): 
        if Port == 'Transmitter':
            self.APx.BenchMode.Setup.SerialDigitalTransmitter.EnableOutputs = state
        else:   #Receiver        
            self.APx.BenchMode.Setup.SerialDigitalReceiver.EnableOutputs = state
                        
    def Configure_Reference(self, Reference):
    
        self.APx.BenchMode.Setup.References.AnalogInputReferences.dBrA.Unit = "Vrms"
        self.APx.BenchMode.Setup.References.AnalogInputReferences.dBrA.Value = Reference

    def Configure_Load(self, Load):
        self.APx.BenchMode.Setup.References.AnalogInputReferences.Watts.Value = Load

    def Configure_Generator(self, Track = True, Level1 = -9999, Level2 = -9999, GenUnit = 'dBV', Freq = 1000, Waveform = 'Sine'):
        self.APx.BenchMode.Generator.Waveform = Waveform
        self.APx.BenchMode.Generator.Levels.Unit = GenUnit
        self.APx.BenchMode.Generator.Levels.TrackFirstChannel = Track
        self.APx.BenchMode.Generator.Levels.SetValue(OutputChannelIndex.Ch1, str(Level1))
        self.APx.BenchMode.Generator.Levels.SetValue(OutputChannelIndex.Ch2, str(Level2))
        self.APx.BenchMode.Generator.Frequency.Value = Freq

    def Configure_Generator_TDM(self, Track = True, Level1 = -9999, GenUnit = 'dBFS', Freq = 1000, Waveform = 'Sine'):
        self.APx.BenchMode.Generator.Waveform = Waveform
        self.APx.BenchMode.Generator.Levels.Unit = GenUnit
        self.APx.BenchMode.Generator.Levels.TrackFirstChannel = Track
        self.APx.BenchMode.Generator.Levels.SetValue(OutputChannelIndex.Ch1, str(Level1))
        self.APx.BenchMode.Generator.Frequency.Value = Freq


    

    def Enable_Generator(self, state = True): 
        if state == True:
           self.APx.BenchMode.Generator.On = True
        else:
           self.APx.BenchMode.Generator.On = False    

    def FilterSel(self, HP_Mode = HP[2], HP_Freq = 20, LP_Mode = LP[0], LP_Freq = 20000, Bandwidth = BW[0], Weighting = Weight[0]):
        self.APx.BenchMode.Setup.HighpassFilter = HP.index(HP_Mode)
        
        if HP_Mode == 'Butterworth' or  HP_Mode == 'Elliptic':
            self.APx.BenchMode.Setup.HighpassFilterFrequency = HP_Freq
        # else:
        #     return(False)
        self.APx.BenchMode.Setup.LowpassFilterAnalog = LP.index(LP_Mode)
        if LP_Mode == 'ADC passband':
            self.APx.BenchMode.Setup.LowpassFilterAnalogBandwidth = BW.index(Bandwidth)
        elif LP_Mode == 'Butterworth' or LP_Mode == 'Elliptic':
            self.APx.BenchMode.Setup.LowpassFilterFrequencyAnalog = LP_Freq
        # else:
        #     return(False)
        self.APx.BenchMode.Setup.WeightingFilter = Weight.index(Weighting)

################################ Meeter ################################### 

    def Read_meter(self, meter_number, channel = 0):
        #channel is the ch - 1
        data = self.APx.BenchMode.Meters.GetReadings(self.APx.BenchMode.Meters.GetMeterType(meter_number))
        return data[channel]

################################ Sweep ###################################


    def Sweep_Configure(self, Source =  SourceSweep['Gen. Level'], StartLevel = -60, StopLevel = 0, Points = 40, Append = False, Repeat = False):
        self.APx.BenchMode.Measurements.SteppedSweep.Show()
        self.APx.BenchMode.Measurements.SteppedSweep.Source = Source
        self.APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Start.Value = StartLevel
        self.APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Stop.Value = StopLevel
        self.APx.BenchMode.Measurements.SteppedSweep.SourceParameters.NumberOfPoints = Points
        self.APx.BenchMode.Measurements.SteppedSweep.Append = Append
        self.APx.BenchMode.Measurements.SteppedSweep.Repeat = Repeat

    def Sweep_Add_Graph(self, Graph = ["RMS Level"]):
        for g in Graph:
            self.APx.BenchMode.Measurements.SteppedSweep.Graphs.Add(g)

    def Sweep_Del_Graph(self, Graph = []):
        if Graph == []:
            count = self.APx.BenchMode.Measurements.SteppedSweep.Graphs.Count
            for i in range(count, 0, -1):
                self.APx.BenchMode.Measurements.SteppedSweep.Graphs.Delete(i-1)
        else:
            for g in Graph:
                self.APx.BenchMode.Measurements.SteppedSweep.Graphs.Delete(g)

    def Sweep_Run(self, Run = True):
        if Run == True:
            self.APx.BenchMode.Measurements.SteppedSweep.Start()
        else:
            self.APx.BenchMode.Measurements.SteppedSweep.Stop()
    
    def Sweep_Clear(self, index = 0):
        self.APx.BenchMode.Measurements.SteppedSweep.ClearData(SourceDataType.Measured, index)

    def Sweep_Export_Data(self, path):
        #   path: write path like r"C:\Users\Smplab\Desktop\pippo.csv"
        settings = self.APx.BenchMode.Measurements.SteppedSweep.CreateExportSettings()
        self.APx.BenchMode.Measurements.SteppedSweep.ExportData(path, settings)

    def Sweep_Save_Image(self, path, item):
        #   path: write path like r"C:\Users\Smplab\Desktop\pippo.jpg"
        #   item is the image to save: index or string name
        #   Ex: if we want to save the RMS Level that  is placed to index 2, item can be or 2 or 'RMS Level'
        img = self.APx.BenchMode.Measurements.SteppedSweep.Graphs.get_Item(item)
        res = img.get_Result()
        xy = res.AsXYGraph()
        xy.FitDataToView()
        img.Save(path, GraphImageType.JPG)
    
    def Sweep_State(self):
        status = self.APx.BenchMode.Measurements.SteppedSweep.IsStarted
        return status

################################ FFT ###################################

    def FFT_Configure(self, Length = FFT_Length[9], BW = Bandwidth[14], avg = 1, Append = False, Repeat = False):
        self.APx.BenchMode.Measurements.Fft.Show()
        self.APx.BenchMode.Measurements.Fft.FFTLength = FFT_Length.index(Length)
        self.APx.BenchMode.Measurements.Fft.AnalogInputBandwidth = Bandwidth.index(BW)
        self.APx.BenchMode.Measurements.Fft.Averages = avg
        self.APx.BenchMode.Measurements.Fft.Append = Append
        self.APx.BenchMode.Measurements.Fft.Repeat = Repeat

    def FFT_axis(self, Xmax, Xmin, Ymax, Ymin):  
        self.APx.BenchMode.Measurements.Fft.FFTSpectrum.XAxis.Minimum = Xmin
        self.APx.BenchMode.Measurements.Fft.FFTSpectrum.XAxis.Maximum = Xmax
        self.APx.BenchMode.Measurements.Fft.FFTSpectrum.YAxis.Minimum = Ymin
        self.APx.BenchMode.Measurements.Fft.FFTSpectrum.YAxis.Maximum = Ymax

    def FFT_Run(self, Run = True):
        if Run == True:
            self.APx.BenchMode.Measurements.Fft.Start()
        else:
            self.APx.BenchMode.Measurements.Fft.Stop() 

    def FFT_Clear(self, index = 0):
        self.APx.BenchMode.Measurements.Fft.ClearData(SourceDataType.Measured, index)

    def FFT_Export_Data(self, path):
        #   path: write path like r"C:\Users\Smplab\Desktop\pippo.csv"
        setting = self.APx.BenchMode.Measurements.Fft.CreateExportSettings()
        self.APx.BenchMode.Measurements.Fft.ExportData(path, setting)

    def FFT_Save_Image(self, path):
        #   path: write path like r"C:\Users\Smplab\Desktop\pippo.jpg"
        self.APx.BenchMode.Measurements.Fft.FFTSpectrum.Save(path, GraphImageType.JPG)

################################ Recorder ###################################

    def Recorder_configure(self, Append = False, Repeat = False, Reading_rate = Read_rate[5]):
        self.APx.BenchMode.Measurements.Recorder.Show()
        self.APx.BenchMode.Measurements.Recorder.Append = Append
        self.APx.BenchMode.Measurements.Recorder.Repeat = Repeat
        self.APx.BenchMode.Measurements.Recorder.ReadingRate = Read_rate.index(Reading_rate)
        self.APx.BenchMode.Measurements.Recorder.Mode = mode = True

    def Recorder_Save_to_file(self, save = False, loacation = '$(MyDocuments)', filename = 'APxRecordedAudio', Replace = False, Format = Format_Wav[0], BitDepth = Bit_Depth[2]):
        self.APx.BenchMode.Measurements.Recorder.SaveAcquisitionToFile = save
        self.APx.BenchMode.Measurements.Recorder.SavedAcquisitionFolderName = location
        self.APx.BenchMode.Measurements.Recorder.SavedAcquisitionFileName = filename
        self.APx.BenchMode.Measurements.Recorder.ReplaceSavedFile = Replace
        self.APx.BenchMode.Measurements.Recorder.SavedAcquisitionAudioType = Format_Wav.index(Format)
        self.APx.BenchMode.Measurements.Recorder.SavedAcquisitionBitDepth = Bit_Depth.index(BitDepth)

    def Recorder_Run(self, Run = True):
        if Run == True:
            self.APx.BenchMode.Measurements.Recorder.Start()
        else:
            self.APx.BenchMode.Measurements.Recorder.Stop() 

    def Recorder_Clear(self, index = 0):
        self.APx.BenchMode.Measurements.Recorder.ClearData(SourceDataType.Measured, index)        

    def Recorder_Export_Data(self, path):
        #   path: write path like r"C:\Users\Smplab\Desktop\pippo.csv"
        setting = self.APx.BenchMode.Measurements.Recorder.CreateExportSettings()
        self.APx.BenchMode.Measurements.Recorder.ExportData(path, setting)

    def Recorder_Save_Image(self, path, item):
        #   path: write path like r"C:\Users\Smplab\Desktop\pippo.jpg"
        #   item is the image to save: index or string name
        #   Ex: if we want to save the RMS Level that  is placed to index 2, item can be or 2 or 'RMS Level'
        img = self.APx.BenchMode.Measurements.Recorder.Graphs.get_Item(item)
        res = img.get_Result()
        xy = res.AsXYGraph()
        xy.FitDataToView()
        img.Save(path, GraphImageType.JPG)


#APx = APx500_Application()
#APx.OperatingMode = False
#APx.Visible = 1
#APx.BenchMode.Setup.OutputConnector.Type =  OutputConnectorType.AnalogUnbalanced
            
# AP = AP555()
# print(BW)
# AP.FilterSel()
# print(HP)