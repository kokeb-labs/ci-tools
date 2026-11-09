// Seeded violation: two pointers to a virtual member function are compared with each other.
#include <cstdint>

namespace kv::rule_13_3_4::bad {

class Device {
 public:
  virtual ~Device() = default;
  virtual std::int32_t start() { return 0; }
  virtual std::int32_t stop() { return 1; }
};

using Action = std::int32_t (Device::*)();

bool is_start(Action a) { return a == &Device::start; }  // seeded

}  // namespace kv::rule_13_3_4::bad
