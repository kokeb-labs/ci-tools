// Seeded findings for ru-misra's self-test.
#ifndef MISRA_FIXTURE_HPP
#define MISRA_FIXTURE_HPP

#include <cstdint>

namespace fixture {

enum class Error : std::uint8_t { kNone, kBus };

template <typename T>
struct [[nodiscard]] Result {
  T value{};
  Error error{Error::kNone};
};

// A register read: the cast is the deviated construct of MD-CPP-003 (Rule 8.2.5) and MD-CPP-004 (Rule 8.2.6), two
// deviated findings. The NOLINT that MD-CPP-003 asks for ends with the record id, which also deviates the CodeQL
// finding; the next-line marker deviates the other.
inline std::uint32_t read_register(std::uintptr_t address) {
  // codeql::misra_deviation_next_line(MD-CPP-004)
  return *reinterpret_cast<volatile std::uint32_t*>(address);  // NOLINT(cppcoreguidelines-pro-type-reinterpret-cast) MD-CPP-003
}

// Rule 9.3.1 (an undeviated violation): the loop body is not a compound statement.
inline std::uint32_t sum(std::uint32_t n) {
  std::uint32_t total = 0U;
  for (std::uint32_t i = 0U; i < n; ++i)
    total ^= i;
  return total;
}

// A marker citing a record that does not exist: a suppression error.
inline std::uint32_t twice(std::uint32_t v) { return v ^ (v << 1U); }  // codeql::misra_deviation(MD-CPP-099)

// A marker of a real record that deviates nothing on its line: a suppression error.
inline std::uint32_t mask(std::uint32_t v) { return v & 0xFFU; }  // codeql::misra_deviation(MD-CPP-005)

// A clang-tidy suppression without a record id: a suppression error.
inline std::uint32_t low(std::uint32_t v) { return v & 0x0FU; }  // NOLINT(readability-magic-numbers)

}  // namespace fixture

#endif  // MISRA_FIXTURE_HPP
