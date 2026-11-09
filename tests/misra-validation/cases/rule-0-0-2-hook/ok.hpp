// Compliant: a function template whose condition calls an optional port hook. The hook's value is
// the port's business; one test port always answers true, another always false. Neither makes the
// condition in the template invariant, and the then-branch is reachable in the guideline's CFG
// (the condition is not a constant expression). The if constexpr is out of scope of both rules.
#ifndef KV_RULE_0_0_X_OK_HOOK_HPP
#define KV_RULE_0_0_X_OK_HOOK_HPP

#include <cstdint>

namespace kv::rule_0_0_x::ok_hook {

enum class Failure : std::uint8_t { Other, AddressNack };
enum class Error : std::uint8_t { Bus, NoDevice };

template <typename Port>
concept HasLastFailure = requires(Port& p, Failure& f) {
  { p.LastFailure(f) } noexcept;
};

template <typename Port>
[[nodiscard]] Error TransferError(Port& port) noexcept {
  if constexpr (HasLastFailure<Port>) {
    Failure failure = Failure::Other;
    if (port.LastFailure(failure) && failure == Failure::AddressNack) {
      return Error::NoDevice;
    }
  } else {
    (void)port;
  }
  return Error::Bus;
}

struct KnowsPort {  // always knows: returns true
  Failure last{Failure::AddressNack};
  bool LastFailure(Failure& f) noexcept {
    f = last;
    return true;
  }
};

struct NeverKnowsPort {  // never knows: returns false
  bool LastFailure(Failure& f) noexcept {
    f = Failure::AddressNack;
    return false;
  }
};

struct NoHookPort {};

inline bool use() noexcept {
  KnowsPort a{};
  NeverKnowsPort b{};
  NoHookPort c{};
  return (TransferError(a) == Error::NoDevice) && (TransferError(b) == Error::Bus) &&
         (TransferError(c) == Error::Bus);
}

}  // namespace kv::rule_0_0_x::ok_hook

#endif  // KV_RULE_0_0_X_OK_HOOK_HPP
