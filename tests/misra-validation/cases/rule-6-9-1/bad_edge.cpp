// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_9_1::bad_edge {

using Ticks = std::uint32_t;
std::uint32_t since(std::uint32_t start);
Ticks since(Ticks start) { return start; }  // the definition uses the alias, the declaration does not

class Clock {
 public:
  Ticks now(Ticks base) const;
};
std::uint32_t Clock::now(std::uint32_t base) const { return base; }

}  // namespace kv::rule_6_9_1::bad_edge
