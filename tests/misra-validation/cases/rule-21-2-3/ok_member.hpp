// Compliant near miss: a member function named system that reports the board's state.
#ifndef KV_RULE_21_2_3_OK_MEMBER_HPP
#define KV_RULE_21_2_3_OK_MEMBER_HPP

#include <cstdint>

namespace kv::rule_21_2_3::ok_member {

enum class State : std::uint8_t { kIdle, kBusy };

struct Board {
  State state{State::kIdle};
  [[nodiscard]] State system() const { return state; }
};

[[nodiscard]] inline bool idle(const Board& board) { return board.system() == State::kIdle; }

}  // namespace kv::rule_21_2_3::ok_member

#endif  // KV_RULE_21_2_3_OK_MEMBER_HPP
