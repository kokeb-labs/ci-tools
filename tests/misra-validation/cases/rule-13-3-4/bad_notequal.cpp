// Seeded violation (notequal): a pointer to a virtual member compared with != against another member's address.
#include <cstdint>

namespace kv::rule_13_3_4::bad_notequal {

class Device {
 public:
  virtual ~Device() = default;
  virtual std::int32_t start() { return 0; }
  virtual std::int32_t stop() { return 1; }
};

using Action = std::int32_t (Device::*)();

bool not_stop(Action a) { return a != &Device::stop; }  // seeded

}  // namespace kv::rule_13_3_4::bad_notequal
