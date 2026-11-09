// Seeded violation: an array owner built from new[], and owners built from new-expressions as call arguments.
#include <cstdint>
#include <memory>

namespace kv::rule_23_11_1::bad_array {

struct Sensor {
  std::int32_t id;
};

std::unique_ptr<std::int32_t[]> buffer() { return std::unique_ptr<std::int32_t[]>(new std::int32_t[4]{}); }  // seeded

std::int32_t sum(const std::shared_ptr<Sensor>& a, const std::shared_ptr<Sensor>& b) { return a->id + b->id; }

std::int32_t pair() {
  return sum(std::shared_ptr<Sensor>(new Sensor{1}),  // seeded
             std::shared_ptr<Sensor>(new Sensor{2}));  // seeded
}

}  // namespace kv::rule_23_11_1::bad_array
