// Seeded violation: two pointers to (possibly virtual) members compared with each other.
#include <cstdint>

namespace kv::rule_13_3_4_variables::bad {

class Device {
 public:
  virtual ~Device() = default;
  virtual std::int32_t start() { return 0; }
  virtual std::int32_t stop() { return 1; }
};

using Action = std::int32_t (Device::*)();

bool differ(Action a, Action b) { return a != b; }

bool differs_from_stop(Action a) { return differ(a, &Device::stop); }

}  // namespace kv::rule_13_3_4_variables::bad
