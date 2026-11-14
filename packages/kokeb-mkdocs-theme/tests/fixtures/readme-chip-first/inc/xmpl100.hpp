// Fixture: the names the capabilities of hardware.yml cite (the API check reads whole words).
class XMPL100 {
 public:
  int EnsureInitialized();
  int SoftReset();
  int HardwareReset();
  int ApplyConfig();
  int SetMode();
  int SetAlertThresholdsC();
  int ReadStatus();
  int ReadRawTemperature();
  int ReadTemperatureC();
  int TriggerOneShot();
  int WaitDataReady();
  int MeasureOnceC();
};
