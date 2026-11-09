// Seeded violation: a destructor calls a virtual function of the object being destroyed.
namespace kv::rule_15_1_1::bad_dtor {

class Sensor {
 public:
  Sensor() = default;
  Sensor(const Sensor&) = delete;
  Sensor(Sensor&&) = delete;
  Sensor& operator=(const Sensor&) = delete;
  Sensor& operator=(Sensor&&) = delete;
  virtual ~Sensor() { shutdown(); }
  virtual void shutdown() {}
};

class Thermistor : public Sensor {
 public:
  void shutdown() override {}
};

}  // namespace kv::rule_15_1_1::bad_dtor
