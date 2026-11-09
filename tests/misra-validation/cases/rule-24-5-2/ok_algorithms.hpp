// Compliant near miss: std::copy, std::equal and std::find on typed ranges.
#ifndef KV_RULE_24_5_2_OK_ALGORITHMS_HPP
#define KV_RULE_24_5_2_OK_ALGORITHMS_HPP

#include <algorithm>
#include <array>
#include <cstdint>

namespace kv::rule_24_5_2::ok_algorithms {

using Frame = std::array<std::uint8_t, 4U>;

inline void copy_frame(Frame& dest, const Frame& source) { static_cast<void>(std::copy(source.begin(), source.end(), dest.begin())); }

[[nodiscard]] inline bool same(const Frame& a, const Frame& b) { return std::equal(a.begin(), a.end(), b.begin()); }

[[nodiscard]] inline bool has_zero(const Frame& f) { return std::find(f.begin(), f.end(), 0U) != f.end(); }

}  // namespace kv::rule_24_5_2::ok_algorithms

#endif  // KV_RULE_24_5_2_OK_ALGORITHMS_HPP
