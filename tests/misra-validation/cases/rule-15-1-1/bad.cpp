// Seeded violation: a constructor calls a virtual function of the object under construction.
namespace kv::rule_15_1_1::bad {

class Sensor {
 public:
  Sensor() { init(); }  // seeded
  Sensor(const Sensor&) = delete;
  Sensor(Sensor&&) = delete;
  Sensor& operator=(const Sensor&) = delete;
  Sensor& operator=(Sensor&&) = delete;
  virtual ~Sensor() = default;
  virtual void init() {}
};

class Thermistor : public Sensor {
 public:
  void init() override {}
};

}  // namespace kv::rule_15_1_1::bad
