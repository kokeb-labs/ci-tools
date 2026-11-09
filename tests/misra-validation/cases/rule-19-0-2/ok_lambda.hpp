// Near miss: a constexpr lambda does the macro's job.
#ifndef KV_RULE_19_0_2_OK_LAMBDA_HPP
#define KV_RULE_19_0_2_OK_LAMBDA_HPP

#include <cstdint>

namespace kv::rule_19_0_2::ok_lambda {

constexpr auto cube = [](std::uint32_t x) -> std::uint32_t { return x * x * x; };

static_assert(cube(2U) == 8U);

[[nodiscard]] inline std::uint32_t volume() { return cube(3U); }

}  // namespace kv::rule_19_0_2::ok_lambda

#endif  // KV_RULE_19_0_2_OK_LAMBDA_HPP
