// Seeded violation: an owner given a new object through reset(new ...), and an array owner from new[].
#include <cstdint>
#include <memory>

namespace kv::rule_23_11_1::bad_reset {

struct Sensor {
  std::int32_t id;
};

void replace(std::unique_ptr<Sensor>& owner) { owner.reset(new Sensor{3}); }

std::unique_ptr<std::int32_t[]> buffer() { return std::unique_ptr<std::int32_t[]>(new std::int32_t[4]{}); }

}  // namespace kv::rule_23_11_1::bad_reset
