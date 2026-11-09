#ifndef KV_RULE_15_1_1_OK_HPP
#define KV_RULE_15_1_1_OK_HPP

// Compliant: the constructor only calls a non-virtual helper; no dynamic dispatch on a half-built object.
#include <cstdint>

namespace kv::rule_15_1_1::ok {

class Sensor {
 public:
  Sensor() { reset(); }
  Sensor(const Sensor&) = delete;
  Sensor(Sensor&&) = delete;
  Sensor& operator=(const Sensor&) = delete;
  Sensor& operator=(Sensor&&) = delete;
  virtual ~Sensor() = default;
  virtual void init() {}

  [[nodiscard]] std::uint32_t state() const { return state_; }

 private:
  void reset() { state_ = 0U; }
  std::uint32_t state_ = 1U;
};

class Thermistor : public Sensor {
 public:
  void init() override {}
};

}  // namespace kv::rule_15_1_1::ok

#endif  // KV_RULE_15_1_1_OK_HPP
