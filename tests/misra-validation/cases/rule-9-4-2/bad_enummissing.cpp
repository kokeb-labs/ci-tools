// Seeded violation (enummissing): a switch over a scoped enum with no default that misses an enumerator.
#include <cstdint>

namespace kv::rule_9_4_2::bad_enummissing {

enum class Mode : std::uint8_t { kIdle, kRun, kStop };

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

}  // namespace kv::rule_9_4_2::bad_enummissing
