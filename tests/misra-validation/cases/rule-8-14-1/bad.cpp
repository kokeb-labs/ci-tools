// Seeded violation: the right operand of && writes to an object that outlives the expression.
#include <cstdint>

namespace kv::rule_8_14_1::bad {

struct Port {
  std::uint32_t reads{0U};
};

bool ready(Port& port, bool enabled) {
  return enabled && (++port.reads > 3U);  // seeded
}

}  // namespace kv::rule_8_14_1::bad
