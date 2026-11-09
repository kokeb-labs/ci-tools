// Seeded violation: a switch over a scoped enumeration lists every enumerator but has no default label. The
// exception for a missing default only covers unscoped enumerations without a fixed underlying type.
#include <cstdint>

namespace kv::rule_9_4_2_scoped_enum::bad {

enum class Mode : std::uint8_t { kIdle, kRun };

std::int32_t cost(Mode m) {
  std::int32_t c = 0;
  switch (m) {  // seeded
    case Mode::kIdle:
      c = 1;
      break;
    case Mode::kRun:
      c = 2;
      break;
  }
  return c;
}

}  // namespace kv::rule_9_4_2_scoped_enum::bad
