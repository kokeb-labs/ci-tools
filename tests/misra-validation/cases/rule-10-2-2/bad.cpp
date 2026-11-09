// Seeded violation: a plain (unscoped) enumeration at namespace scope.
#include <cstdint>

namespace kv::rule_10_2_2::bad {

enum Colour : std::uint8_t { kRed, kGreen };  // seeded

Colour other(Colour c) { return (c == kRed) ? kGreen : kRed; }

}  // namespace kv::rule_10_2_2::bad
