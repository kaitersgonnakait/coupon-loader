"""Just a quick script to load up on all available coupons."""

import load_giant_coupons
import load_safeway_coupons

def main():
    load_giant_coupons.main()
    load_safeway_coupons.main()
    print('ALL DONE')


if __name__ == '__main__':
    main()
