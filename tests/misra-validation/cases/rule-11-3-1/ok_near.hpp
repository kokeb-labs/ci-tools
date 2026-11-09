// Near misses (near): std::array everywhere; a string literal is not a declared array.
#ifndef KV_RULE_11_3_1_OK_NEAR_HPP
#define KV_RULE_11_3_1_OK_NEAR_HPP

#include <array>
#include <cstdint>
#include <string_view>

namespace kv::rule_11_3_1::ok_near {

struct Frame {
  std::array<std::uint32_t, 4> payload{};
};

inline constexpr std::array<std::array<std::uint32_t, 2>, 2> kTable{{{1U, 2U}, {3U, 4U}}};

inline std::uint32_t corner(const Frame& f) { return f.payload[0] | kTable[1][1]; }

inline std::string_view name() { return "frame"; }

}  // namespace kv::rule_11_3_1::ok_near

#endif  // KV_RULE_11_3_1_OK_NEAR_HPP
