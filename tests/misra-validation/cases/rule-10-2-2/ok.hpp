// Compliant: a scoped enumeration.
#ifndef KV_RULE_10_2_2_OK_HPP
#define KV_RULE_10_2_2_OK_HPP

#include <cstdint>

namespace kv::rule_10_2_2::ok {

enum class Colour : std::uint8_t { kRed, kGreen };

inline Colour other(Colour c) { return (c == Colour::kRed) ? Colour::kGreen : Colour::kRed; }

}  // namespace kv::rule_10_2_2::ok

#endif  // KV_RULE_10_2_2_OK_HPP
