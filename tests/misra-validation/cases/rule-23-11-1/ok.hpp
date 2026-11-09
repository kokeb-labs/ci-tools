// Compliant: the factory functions create the object and its owner in one step.
#ifndef KV_RULE_23_11_1_OK_HPP
#define KV_RULE_23_11_1_OK_HPP

#include <cstdint>
#include <memory>

namespace kv::rule_23_11_1::ok {

struct Sensor {
  std::int32_t id;
};

[[nodiscard]] inline std::unique_ptr<Sensor> make_unique_sensor() { return std::make_unique<Sensor>(Sensor{1}); }

[[nodiscard]] inline std::shared_ptr<Sensor> make_shared_sensor() { return std::make_shared<Sensor>(Sensor{2}); }

[[nodiscard]] inline std::int32_t id_of(const Sensor& sensor) { return sensor.id; }

}  // namespace kv::rule_23_11_1::ok

#endif  // KV_RULE_23_11_1_OK_HPP
