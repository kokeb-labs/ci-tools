// Compliant: typed copies and comparisons of the whole object.
#ifndef KV_RULE_24_5_2_OK_HPP
#define KV_RULE_24_5_2_OK_HPP

#include <array>
#include <cstdint>

namespace kv::rule_24_5_2::ok {

using Frame = std::array<std::uint8_t, 4U>;

inline void copy_frame(Frame& dest, const Frame& source) { dest = source; }

[[nodiscard]] inline bool same_frame(const Frame& a, const Frame& b) { return a == b; }

}  // namespace kv::rule_24_5_2::ok

#endif  // KV_RULE_24_5_2_OK_HPP
