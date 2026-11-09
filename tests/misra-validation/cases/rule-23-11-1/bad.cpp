// Seeded violation: smart pointers built from a separate new-expression.
#include <cstdint>
#include <memory>

namespace kv::rule_23_11_1::bad {

struct Sensor {
  std::int32_t id;
};

std::unique_ptr<Sensor> make_unique_sensor() { return std::unique_ptr<Sensor>(new Sensor{1}); }

std::shared_ptr<Sensor> make_shared_sensor() { return std::shared_ptr<Sensor>(new Sensor{2}); }

}  // namespace kv::rule_23_11_1::bad
